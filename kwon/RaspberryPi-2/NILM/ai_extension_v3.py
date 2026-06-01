#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_extension_v4_pending_event_guarded.py
========================================

WattsUp NILM Multi-tap 추론 엔진 v4.

v3 대비 핵심 수정
-----------------
1) ON 이벤트 즉시 분류 제거
   - ON 이벤트가 감지되면 곧바로 소켓에 등록하지 않고 PENDING_ON 상태로 둔다.
   - 몇 frame 기다린 뒤 안정된 window에서 분류한다.
   - 청소기/드라이기처럼 기동 과도 구간이 큰 기기를 TV/충전기로 오분류하는 문제를 줄인다.

2) ON SKIP 제거
   - 분류 결과가 이미 active인 기기여도 바로 버리지 않는다.
   - range sanity와 absolute RF를 다시 비교해 다른 신규 기기 후보가 있으면 그 기기로 등록한다.

3) class_ranges 기반 sanity filter 추가
   - rf_device_features.json의 Irms/H1/P_proxy 범위를 사용한다.
   - 예: RF_delta가 TV라고 해도 H1이 TV 범위를 크게 넘으면 TV 후보를 거절한다.

4) OFF는 RF_removed보다 signature matching 우선
   - 각 기기가 ON 될 때의 dIrms/dH1/dPabs signature를 저장한다.
   - OFF 이벤트에서는 현재 감소량과 가장 가까운 active device를 먼저 제거한다.

5) pending 중 baseline freeze
   - 기기가 들어오는 동안 baseline이 새 부하를 먹어버리는 문제를 방지한다.

주의
----
- CT/PT가 전체 1개라면 실제 물리 소켓 번호를 맞추는 코드는 아니다.
- Socket 1~4는 UI 표시 슬롯이다.
"""

import os
import sys
import json
import logging
import datetime
import time
from collections import deque

import numpy as np
import pandas as pd
import joblib

# main.py는 RaspberryPi 폴더에서 실행되고, 이 파일은 RaspberryPi/NILM 안에 있습니다.
# 따라서 main.py를 바꾸지 않아도 NILM 내부 모듈을 확실히 찾도록 현재 폴더를 import 경로에 추가합니다.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from dsp_engine import DSPEngine
from feature_extractor import (
    extract_frame_features,
    aggregate_window_features,
    WINDOW_SIZE,
)

AI_VERSION = "ai_extension_2026_05_31_v100_h5_off_match_and_weak_lp_off"

# =====================================================================
# 경로 / 상수
# =====================================================================

def find_model_dir():
    base = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()
    paths = [
        os.path.join(base, "Model"),
        os.path.join(base, "..", "Model"),
        os.path.join(base, "..", "..", "Model"),
        os.path.join(cwd, "Model"),
        os.path.join(cwd, "..", "Model"),
        os.path.join(cwd, "..", "..", "Model"),
    ]
    for p in paths:
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "rf_device_classifier.joblib")):
            return os.path.abspath(p)
    return os.path.abspath(os.path.join(base, "..", "Model"))


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = find_model_dir()
MODEL_PATH = os.path.join(MODEL_DIR, "rf_device_classifier.joblib")
FEATURES_PATH = os.path.join(MODEL_DIR, "rf_device_features.json")

N_SOCKETS = 4

# 이벤트 판정 임계값
IRMS_NOISE_FLOOR = 3.0
IRMS_DEVICE_MIN = 6.0
H1_DEVICE_MIN = 40.0
IRMS_RESISTIVE_MIN = 15.0
SANITY_CHECK_H1_MIN = 500.0

# 이벤트/대기 frame 설정
EVENT_COOLDOWN_FRAMES = 6
PENDING_ON_FRAMES = 8          # ON 감지 후 안정 창을 기다리는 frame 수
RECLASSIFY_DELAY = WINDOW_SIZE # 등록 후 signature 갱신용

# v53: OFF verify (orchestrator 토글 검증) cancel 시 cooldown.
# 모든 OFF 후보가 false (= 부하 여전 살아있음) 판명나서 active_devices 그대로
# 두기로 결정한 경우, 같은 drop 으로 다시 OFF event 가 fire 되지 않도록 길게.
OFF_VERIFY_CANCEL_COOLDOWN_FRAMES = 30

# Baseline EMA
EMA_ALPHA = 0.2

# Window 큐
FRAME_QUEUE_SIZE = WINDOW_SIZE
MIN_FRAMES_FOR_DECISION = WINDOW_SIZE

# RF 신뢰도
RF_CONFIDENCE_THRESHOLD = 0.55
RECLASSIFY_CONF = 0.45

# 가전별 표시 전력
DEVICE_REAL_POWER_W = {
    "charger": 5.0,
    "tv": 60.0,
    "cleaner": 600.0,
    "dryer": 1800.0,
    "microwave": 900.0,
}

# charger/tv boundary. 단, v4에서는 high-power 후보에는 적용하지 않는다.
CHARGER_TV_H1_BOUNDARY = 1100.0
CHARGER_TV_H1_CORRECTION_MAX = 2500.0

# 시작 시 기기가 켜져 있는지 판단
STARTUP_DEVICE_IRMS_MIN = 30.0
STARTUP_DEVICE_H1_MIN = 300.0

# range sanity 설정
RANGE_MARGIN = 0.35       # class range 밖 허용 여유
RANGE_GOOD_SCORE = 0.65   # 이보다 낮으면 range가 꽤 잘 맞는 후보
RANGE_OK_SCORE = 1.15     # 이보다 낮으면 허용 가능한 후보

HIGH_POWER_DEVICES = {"cleaner", "dryer", "microwave"}
LOW_POWER_DEVICES = {"charger", "tv"}

# v6 판정 보정값: 현재 실측 로그 기준
LOW_POWER_DI_MAX = 45.0
LOW_POWER_DH1_MAX = 2400.0
LOW_POWER_PABS_MAX = 25000.0
LOW_POWER_TINY_DH1 = 250.0
CLEANER_DI_MIN = 50.0
CLEANER_DI_MAX = 250.0
CLEANER_DH1_MIN = 3500.0
CLEANER_DH1_MAX = 12000.0
DRYER_STRONG_DI = 250.0
DRYER_STRONG_DH1 = 14000.0
MICROWAVE_DI_MIN = 200.0
MICROWAVE_DH1_MIN = 12000.0

# v7 OFF 보호 로직
# high-power(cleaner/dryer/microwave)가 켜져 있을 때 발생하는 작은 H1 감소를
# charger/tv OFF로 잘못 처리하지 않기 위한 기준.
LOW_POWER_OFF_WHILE_HIGHPOWER_GUARD_H1 = 1800.0
LOW_POWER_OFF_WHILE_HIGHPOWER_GUARD_I = 35.0
HIGHPOWER_PARTIAL_OFF_MIN_H1 = 180.0
HIGHPOWER_PARTIAL_OFF_MIN_I = 5.0

# v9: charger/tv처럼 Irms 변화는 애매하거나 오히려 내려가는데 H1만 길게 상승하는 경우가 있다.
# 단, high-power active 여부만으로 막으면 순서 의존성이 생긴다.
# 그래서 "high-power가 켜져 있느냐"가 아니라
# "현재 H1-only 변화가 active high-power의 ramp/mode 변화로 설명 가능한가"를 본다.
H1_ONLY_ON_MIN = 300.0
H1_ONLY_ON_MAX = 2600.0
H1_ONLY_ON_MIN_DI = -45.0
H1_ONLY_ON_MAX_DI = 45.0
H1_ONLY_DPABS_MAX = 35000.0
HIGH_POWER_RAMP_GUARD_FRAMES = 18
HIGH_POWER_MODE_DPABS_GUARD = 45000.0

# v10: charger/tv 같은 저전력 기기는 H1 ramp가 길고 high-power OFF 직후 잔향에
# 끌려가서 가짜 OFF가 쉽게 생긴다.
# - 켠 지 얼마 안 된 charger/tv는 OFF 금지
# - cleaner/dryer/microwave OFF 직후 일정 시간 동안 charger/tv OFF 금지
LOW_POWER_MIN_ACTIVE_FRAMES_BEFORE_OFF = 85
LOW_POWER_OFF_AFTER_HIGHPOWER_GUARD_FRAMES = 28
LP_OFF_AFTER_LOWPOWER_GUARD_FRAMES = 20  # v81: LP relay OFF 후 잔류 신호로 다른 LP가 잘못 OFF되는 것 방지
LOW_POWER_OFF_MIN_DROP_H1 = 220.0
LOW_POWER_OFF_MIN_DROP_I = 4.0

# v11 수정: 마지막 TV OFF만 보정한다.
# TV가 active이고 high-power가 모두 꺼진 뒤 안정화된 상태에서
# 중간 크기의 H1 감소가 보이면 charger보다 TV OFF를 우선한다.
TV_OFF_ONLY_MIN_DROP_H1 = 650.0
TV_OFF_ONLY_MAX_DROP_H1 = 1700.0
TV_OFF_ONLY_MIN_DROP_I = 4.0
TV_OFF_ONLY_MIN_TV_AGE_FRAMES = 85
TV_OFF_ONLY_AFTER_HIGHPOWER_FRAMES = 28

# v52d: LP RAMP CONTINUATION swap (v70 디자인 재도입)
# HP 다중 active 상황에서 TV ramp 가 ~10초에 걸쳐 분리된 두 ON event 로 잡히는 경우
# (실측 2026-05-27 15:01:39 → 15:01:48: 1단계 dH1=1049 → charger 오분류, 2단계
# dH1=1452 → tv 정분류. 같은 TV 의 ramp 인데 두 LP 가전으로 잘못 잡힘) 보정.
#
# 조건: chosen 이 LP 이고 (charger/tv 짝) 안에서 다른 LP 가 이미 active 이고
# 그 등록이 신호-only fallback (`low_power_h1_over_rf_*`, `low_power_h1_only`) 였다면
# 같은 가전의 ramp 연속으로 보고 새 socket 매핑 대신 기존 라벨 swap.
LOW_POWER_RAMP_CONTINUATION_SECONDS = 15.0
LP_RAMP_SWAP_OLD_METHODS = {
    "low_power_h1_over_rf_delta",
    "low_power_h1_over_rf_delta_hp",
    "low_power_h1_over_rf_abs",
    "low_power_h1_over_rf_abs_hp",
    "low_power_h1_only",
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
_LOG_DIR = os.path.dirname(os.path.abspath(__file__))
_LOG_FILE = os.path.join(
    _LOG_DIR,
    f"nilm_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
)
_fh = logging.FileHandler(_LOG_FILE, encoding='utf-8')
_fh.setLevel(logging.INFO)
_fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logging.getLogger().addHandler(_fh)
logging.info(f"[AI VERSION] {AI_VERSION}")
logging.info(f"[LOG FILE] {_LOG_FILE}")


# =====================================================================
# SocketFSM
# =====================================================================

class SocketFSM:
    VALID_STATES = {"EMPTY", "DEVICE_ON", "DEVICE_OFF"}

    def __init__(self, idx):
        self.idx = idx
        self.state = "EMPTY"
        self.device = None
        self.power_w = 0.0

    def assign_device(self, device_name, power_w):
        self.device = device_name
        self.state = "DEVICE_ON"
        self.power_w = power_w

    def turn_off(self):
        if self.state == "DEVICE_ON":
            self.state = "DEVICE_OFF"
            self.power_w = 0.0

    def reset_to_empty(self):
        self.state = "EMPTY"
        self.device = None
        self.power_w = 0.0

    def to_dict(self):
        return {
            "idx": self.idx,
            "state": self.state,
            "device": self.device,
            "power_w": self.power_w,
        }


# =====================================================================
# AIEngine
# =====================================================================

class AIEngine(DSPEngine):
    def __init__(self, spi_core, buffer_size=150):
        super().__init__(spi_core, buffer_size=buffer_size)

        self.model = joblib.load(MODEL_PATH)
        with open(FEATURES_PATH, encoding="utf-8") as f:
            self.info = json.load(f)

        self.feature_names = list(self.info["feature_names"])
        self.class_ranges = self.info.get("class_ranges", {})
        self.device_prototypes = self.info.get("device_prototypes", {})

        logging.info(f"Model loaded. classes={list(self.model.classes_)}")
        logging.info(f"Feature count: {len(self.feature_names)}")
        logging.info(f"Model dir: {MODEL_DIR}")

        print("\n" + "=" * 68)
        print("WattsUp NILM 테스트 프로토콜 v9")
        print("=" * 68)
        print("중요: 시작 전에 모든 기기를 콘센트에서 빼두세요.")
        print("[INIT BASELINE] 확인 후 각 단계는 8초 이상 기다려 주세요.")
        print("A 충전기 ON → B TV ON → C 청소기 ON → D 청소기 OFF")
        print("E 드라이기 ON → F 드라이기 OFF → G 전자레인지 ON → H 전자레인지 OFF")
        print("I TV OFF → J 충전기 OFF")
        print("=" * 68 + "\n")

        self.frame_feats = deque(maxlen=FRAME_QUEUE_SIZE)

        self.baseline_feat = None
        self.baseline_irms = 0.0
        self.baseline_h1 = 0.0
        self.idle_baseline_irms = 0.0
        self.idle_baseline_h1 = 0.0

        self.device_signatures = {}  # dev -> {delta_irms, delta_h1, delta_pabs}
        # v29: OFF 시 sig 를 백업해두고 같은 라벨 재등록 때 sig 가 dominance 로 작게 측정되면
        # 더 큰 백업 sig 사용. 실측: cleaner + dryer active 중 charger 재등록 시 sig dH1=430 으로
        # 작게 잡혀 그 후 charger OFF cascade 가 영역(0.30-1.50) 벗어나 tv 가 잘못 force OFF.
        # 백업 sig dH1=978 (Phase 1 측정값) 을 유지하면 매칭 정확.
        self.device_signatures_history = {}
        # v30: cascade 동안 drop_h1 추이 저장. 진짜 OFF event 면 마지막 drop ≈ max
        # (점진적 증가). cleaner duty cycle noise 면 진동/감소 → cascade break 시 sig 매칭 skip.
        self._cascade_drop_history = []
        self.active_devices = {}     # dev -> socket idx
        self.sockets = [SocketFSM(i + 1) for i in range(N_SOCKETS)]
        self._socket_prior_state = {}

        self.pre_event_baseline_irms = 0.0
        self.pre_event_baseline_h1 = 0.0
        self.pre_event_baseline_feat = None

        self.pending_on = None
        self.reclassify_countdown = 0
        self.event_cooldown = 0
        self.frame_count = 0
        self.event_history = deque(maxlen=80)

        # v9: high-power 기동/모드 변경 직후 H1-only 변화를 low-power로 오인하지 않기 위한 기록.
        # 이 값은 순서 의존적으로 low-power를 막는 용도가 아니라,
        # 최근 high-power ramp 구간만 잠깐 보호하는 용도다.
        self.last_high_power_event_frame = -10**9
        self.last_high_power_off_frame = -10**9
        self.last_lp_off_frame = -10**9  # v81: LP OFF 후 잔류 가드용
        self.device_on_frames = {}
        # v52d: LP RAMP CONTINUATION 의 elapsed 판정용 wall-clock 기록.
        # frame_count 는 SPI 부하로 fs 변동이 커서 시간 환산 부정확.
        self.device_on_wallclock = {}

        # v46: HP OFF 후 baseline 안정화 시점에 active LP 실제 존재 검증.
        # 실측 (2026-05-24 19:42): microwave dominant 중 charger ramp 초기 sig=452.8
        # (정상 800 대비 underestimate) 로 등록 → 사용자가 charger 뺐을 때 cascade drops
        # 가 microwave 노이즈에 묻혀 force off 못함. microwave OFF 후 baseline=171
        # (idle 수준) 이므로 charger 가 실제로 빠진 게 명확. 30 frame 뒤 baseline
        # 검증으로 자동 cleanup.
        self._hp_off_lp_cleanup_frame = 0

        # v12: partial-drop OFF reject 시 baseline 동결 (drop 누적 대기)
        # multi-active(charger+tv) 상태에서 TV unplug 의 초기 부분 drop(d_h1=475)이
        # sig 작은 charger(sig=1130)에 더 가깝게 score 가 나와 charger 가 잘못 OFF 되는 문제.
        # 이후 cooldown 동안 baseline 이 잔향을 흡수해서 두 번째 OFF event 도 부정확해진다.
        # → REJECT 후 baseline 을 frozen 유지하면 다음 frame 의 d_h1 이 TV 전체 drop 으로 누적되어
        #   올바르게 TV OFF 로 분류됨.
        self._pending_off_drop = False

        # v15: OFF REJECT 사유 기록 - baseline 동결 여부 결정에 사용
        # "partial": 부분 drop, 실제 OFF 진행 중 → 동결 (누적 대기)
        # "oversized"/"guarded"/None: drain 잔향/노이즈 → 동기화 (cascade 종료)
        self._off_reject_reason = None

        # v18: 연속 partial reject 카운터. drop 이 안 자라는 stable cascade 차단용.
        self._consecutive_partial_rejects = 0

        self._last_ch0 = np.zeros(buffer_size)
        self._last_ch1 = np.zeros(buffer_size)
        self._last_fs = 0.0

        # v53: OFF verify callback hook (orchestrator 가 init 시 등록).
        # _handle_device_off 가 후보 결정 직후 호출. signature (dev, drop, win_feat) → verdict
        # verdict ∈ {"confirm", "reject", "cancel"}:
        #   confirm: 토글 결과 부하 없음 → 진짜 OFF, 기존 흐름대로 active_devices 에서 제거
        #   reject : 토글 결과 부하 여전 → false OFF, dev 를 exclude 에 추가하고 재선출
        #   cancel : 더 이상 후보 없거나 매핑 lookup 실패 → active_devices 그대로 유지,
        #            baseline sync + cooldown 만 (cascade 방어)
        # None 이면 callback 비활성화 (legacy 동작).
        self._off_verify_callback = None

        # v54: exhaust fallback hook (orchestrator 가 init 시 등록).
        # 첫 검증 reject + 재선출 모두 실패 (cancel) 직전에 마지막으로 호출.
        # signature: (drop, win_feat, excluded) → fallback_dev (str) or None
        # 동작: 모든 ASSIGNED socket 전수 토글 → 부재 socket 의 dev 반환.
        # 사용자 원래 직감 알고리즘 (cancel 직전 전수 검색) 구현.
        self._off_verify_exhaust_fallback = None

    # ------------------------------------------------------------------
    # Main frame processing
    # ------------------------------------------------------------------
    def process_ai_frame(self):
        ch0, ch1, ts, fs_actual = self.process_raw_mode()
        self._last_ch0 = ch0
        self._last_ch1 = ch1
        self._last_fs = fs_actual

        frame_feat = extract_frame_features(ch0, ch1, fs_actual)
        self.frame_feats.append(frame_feat)
        self.frame_count += 1

        if len(self.frame_feats) < MIN_FRAMES_FOR_DECISION:
            return self._make_status("WARMUP", None)

        win_feat = aggregate_window_features(list(self.frame_feats))

        if self.baseline_feat is None:
            self._init_baseline(win_feat)
            return self._make_status("INIT", win_feat)

        # pending ON 중에는 baseline을 절대 업데이트하지 않는다.
        if self.pending_on is not None:
            event = self._process_pending_on(win_feat)
            return self._make_status(event, win_feat)

        if self.event_cooldown > 0:
            self.event_cooldown -= 1

        event = self._classify_event(win_feat)

        if event == "DEVICE_ON":
            self._start_pending_on(win_feat)
            event = "PENDING_ON"
        elif event == "DEVICE_OFF":
            self._handle_device_off(win_feat)
        else:
            self._update_baseline(win_feat)

        return self._make_status(event, win_feat)

    def _init_baseline(self, win_feat):
        self.baseline_feat = dict(win_feat)
        self.baseline_irms = float(win_feat.get("Irms_adc_mean", 0.0))
        self.baseline_h1 = float(win_feat.get("H1_60_mag_mean", 0.0))
        self.idle_baseline_irms = self.baseline_irms
        self.idle_baseline_h1 = self.baseline_h1

        logging.info(f"[INIT BASELINE] Irms={self.baseline_irms:.2f}, H1={self.baseline_h1:.2f}")

        if self.baseline_irms > STARTUP_DEVICE_IRMS_MIN and self.baseline_h1 > STARTUP_DEVICE_H1_MIN:
            logging.info("[STARTUP] 기기가 이미 켜진 상태로 보입니다. startup detection 수행.")
            self.baseline_feat = {k: 0.0 for k in self.feature_names}
            self.baseline_irms = 0.0
            self.baseline_h1 = 0.0
            self._register_device_from_stable_window(win_feat, reason="startup")
        elif self.baseline_irms > STARTUP_DEVICE_IRMS_MIN:
            logging.info(
                f"[STARTUP] Irms={self.baseline_irms:.2f} 높지만 H1={self.baseline_h1:.2f} < {STARTUP_DEVICE_H1_MIN} "
                "→ 센서 idle 오프셋으로 처리."
            )

    # ------------------------------------------------------------------
    # Event detection
    # ------------------------------------------------------------------
    def _classify_event(self, win_feat):
        if self.event_cooldown > 0:
            return "IDLE"

        irms_now = float(win_feat.get("Irms_adc_mean", 0.0))
        h1_now = float(win_feat.get("H1_60_mag_mean", 0.0))

        d_irms = irms_now - self.baseline_irms
        d_h1 = h1_now - self.baseline_h1

        abs_d_irms = abs(d_irms)
        abs_d_h1 = abs(d_h1)

        if abs_d_irms < IRMS_NOISE_FLOOR and abs_d_h1 < H1_DEVICE_MIN * 0.5:
            return "IDLE"

        # v9 핵심 보정:
        # charger/tv는 센서 Irms 오프셋 때문에 dI가 음수/애매한데 H1만 상승하는 경우가 있다.
        # 다만 high-power가 active라는 이유만으로 막으면,
        # dryer→charger→tv 같은 순서에서 저전력 기기를 아예 못 잡는다.
        # 따라서 H1-only 후보를 먼저 만들고, active high-power의 ramp/mode 변화로 설명될 때만 막는다.
        d_pabs = (
            float(win_feat.get("Pabs_mean_proxy_mean", win_feat.get("Pabs_mean_proxy", 0.0)))
            - float(self.baseline_feat.get("Pabs_mean_proxy_mean", self.baseline_feat.get("Pabs_mean_proxy", 0.0)))
        )
        h1_only_low_power_on = (
            H1_ONLY_ON_MIN <= d_h1 <= H1_ONLY_ON_MAX
            and H1_ONLY_ON_MIN_DI <= d_irms <= H1_ONLY_ON_MAX_DI
            and abs(d_pabs) <= H1_ONLY_DPABS_MAX
        )
        if h1_only_low_power_on:
            if self._h1_only_explained_by_active_high_power(d_irms, d_h1, d_pabs):
                logging.info(
                    f"[H1-ONLY REJECT] active high-power ramp/mode explains change | "
                    f"d_irms={d_irms:.1f}, d_h1={d_h1:.1f}, d_pabs={d_pabs:.1f}"
                )
            else:
                logging.info(
                    f"[EVENT-TRIG] h1-only low-power ON d_irms={d_irms:.1f}, "
                    f"d_h1={d_h1:.1f}, d_pabs={d_pabs:.1f}"
                )
                return "DEVICE_ON"

        if abs_d_irms >= IRMS_DEVICE_MIN and abs_d_h1 >= H1_DEVICE_MIN:
            if d_irms > 0 and d_h1 > 0:
                logging.info(f"[EVENT-TRIG] cond2 ON d_irms={d_irms:.1f}, d_h1={d_h1:.1f}")
                return "DEVICE_ON"

            # v6: OFF는 전류와 H1이 모두 실제로 감소할 때만 인정한다.
            # 이전 v5는 d_irms<0이면서 d_h1>0인 H1 상승/ramp 구간도 strong_both로 OFF 처리해서
            # TV/charger가 엉뚱하게 OFF 되는 문제가 있었다.
            strong_both = (d_irms < 0 and d_h1 < 0
                           and abs_d_irms >= IRMS_DEVICE_MIN * 2
                           and abs_d_h1 >= H1_DEVICE_MIN * 2)
            strong_h1 = d_h1 < 0 and abs_d_h1 >= H1_DEVICE_MIN * 5
            if d_irms < 0 and d_h1 < 0 and (strong_both or strong_h1):
                logging.info(f"[EVENT-TRIG] cond2 OFF d_irms={d_irms:.1f}, d_h1={d_h1:.1f}")
                return "DEVICE_OFF"

            logging.info(f"[OFF-REJECT] cond2 d_irms={d_irms:.1f}, d_h1={d_h1:.1f} (transient 가능성)")

        # v7: Irms만 증가했더라도 H1이 음수로 감소 중이면 ON으로 보지 않는다.
        # 이전에는 dI>0, dH1<0인 잔향 구간이 PENDING_ON으로 들어가서 상태가 꼬일 수 있었다.
        if abs_d_irms >= IRMS_RESISTIVE_MIN and d_irms > 0 and d_h1 >= 0:
            logging.info(f"[EVENT-TRIG] cond3 ON d_irms={d_irms:.1f}, d_h1={d_h1:.1f}")
            return "DEVICE_ON"

        if self.frame_count % 4 == 0:
            logging.info(
                f"[NEAR-MISS] d_irms={d_irms:.1f}, d_h1={d_h1:.1f}, "
                f"baseline_irms={self.baseline_irms:.1f}, baseline_h1={self.baseline_h1:.1f}"
            )
        return "IDLE"

    def _h1_only_explained_by_active_high_power(self, d_irms, d_h1, d_pabs):
        """
        H1-only 저전력 후보가 active high-power의 자연스러운 변동인지 판단한다.

        핵심 원칙:
        - high-power가 active라는 이유만으로 charger/tv 감지를 막지 않는다.
        - 단, high-power ON/모드 변경 직후의 ramp 구간이거나, Pabs 변화가 너무 크면
          low-power 추가가 아니라 high-power 변동으로 본다.
        """
        high_active = [d for d in self.active_devices if d in HIGH_POWER_DEVICES]
        if not high_active:
            return False

        # high-power 등록/모드변경 직후에는 내부 ramp가 남아 있을 가능성이 크다.
        if self.frame_count - self.last_high_power_event_frame <= HIGH_POWER_RAMP_GUARD_FRAMES:
            return True

        # H1만 상승한 것처럼 보여도 Pabs가 크게 움직이면 저전력 추가라기보다
        # dryer/cleaner/microwave의 모드 변화나 duty-cycle 변화일 가능성이 높다.
        if abs(d_pabs) >= HIGH_POWER_MODE_DPABS_GUARD:
            return True

        # active high-power signature 대비 아주 작은 흔들림은 baseline/ramp 잔향으로 흡수한다.
        max_sig_h1 = 0.0
        max_sig_i = 0.0
        for dev in high_active:
            sig = self.device_signatures.get(dev, {})
            max_sig_h1 = max(max_sig_h1, abs(float(sig.get("delta_h1", 0.0))))
            max_sig_i = max(max_sig_i, abs(float(sig.get("delta_irms", 0.0))))

        if max_sig_h1 > 0 and d_h1 < max(450.0, max_sig_h1 * 0.04) and abs(d_irms) < max(8.0, max_sig_i * 0.03):
            return True

        return False

    # ------------------------------------------------------------------
    # Pending ON
    # ------------------------------------------------------------------
    def _start_pending_on(self, win_feat):
        if self.pending_on is not None:
            return

        self.pending_on = {
            "wait": PENDING_ON_FRAMES,
            "start_frame": self.frame_count,
            "pre_baseline_feat": dict(self.baseline_feat) if self.baseline_feat else None,
            "pre_baseline_irms": self.baseline_irms,
            "pre_baseline_h1": self.baseline_h1,
            "first_feat": dict(win_feat),
        }
        logging.info(
            f"[PENDING ON] start frame={self.frame_count}, wait={PENDING_ON_FRAMES}, "
            f"pre_I={self.baseline_irms:.1f}, pre_H1={self.baseline_h1:.1f}"
        )

    def _process_pending_on(self, win_feat):
        self.pending_on["wait"] -= 1
        if self.pending_on["wait"] > 0:
            return "PENDING_ON"

        pending = self.pending_on
        self.pending_on = None
        self._register_device_from_stable_window(win_feat, reason="pending_on", pending=pending)
        return "DEVICE_ON"

    def _register_device_from_stable_window(self, win_feat, reason="pending_on", pending=None):
        if pending is None:
            pre_feat = dict(self.baseline_feat) if self.baseline_feat else {k: 0.0 for k in self.feature_names}
            pre_irms = self.baseline_irms
            pre_h1 = self.baseline_h1
        else:
            pre_feat = pending.get("pre_baseline_feat") or {k: 0.0 for k in self.feature_names}
            pre_irms = float(pending.get("pre_baseline_irms", self.baseline_irms))
            pre_h1 = float(pending.get("pre_baseline_h1", self.baseline_h1))

        # v43: pre_baseline 이 active devices sig 합 대비 비정상적으로 낮으면 보정.
        # 실측 (2026-05-24 18:59:49): TV (sig=1378) active 중 사용자가 charger 꽂았는데
        # pre_H1=190 (idle 수준) → d_h1 = win-pre = 2185-190 = 1995 (tv 영역으로 잘못 해석).
        # 원인: TV ON 직후 ORCH 가 toggle-id 로 소켓 4개를 차례로 OFF/ON 하면서 TV 가 잠시
        # 꺼졌고, baseline EMA 가 낮은 H1 을 따라간 뒤 안정화 시간 부족. 정상 baseline ≈
        # idle + tv_sig = 1438 로 보정하면 d_h1 = 747 → 정확한 charger 영역.
        if self.active_devices and self.idle_baseline_h1 > 0:
            sum_active_sig_h1 = sum(
                abs(float(self.device_signatures.get(d, {}).get("delta_h1", 0.0)))
                for d in self.active_devices
            )
            expected_baseline_h1 = self.idle_baseline_h1 + sum_active_sig_h1
            if expected_baseline_h1 > 0 and pre_h1 < expected_baseline_h1 * 0.80:
                sum_active_sig_irms = sum(
                    abs(float(self.device_signatures.get(d, {}).get("delta_irms", 0.0)))
                    for d in self.active_devices
                )
                expected_baseline_irms = self.idle_baseline_irms + sum_active_sig_irms
                logging.info(
                    f"[PRE-BASELINE FIX] pre_H1={pre_h1:.1f} < 80% of expected={expected_baseline_h1:.1f} "
                    f"(idle={self.idle_baseline_h1:.1f} + active sigs={sum_active_sig_h1:.1f}); "
                    f"ORCH toggle drift 추정, 보정 → pre_H1={expected_baseline_h1:.1f}, "
                    f"pre_I={expected_baseline_irms:.1f}"
                )
                pre_h1 = expected_baseline_h1
                pre_irms = expected_baseline_irms
                pre_feat = dict(pre_feat)
                pre_feat["H1_60_mag_mean"] = pre_h1
                pre_feat["Irms_adc_mean"] = pre_irms

        # v26: PENDING ON 트리거 시점에는 cond2 ON (d_h1 양수) 이었지만 8 프레임 정착 후
        # d_h1 가 명백히 음수이면 transient ON 트리거였음 → OFF pathway 로 reroute.
        # 실측 (2026-05-22 16:11:32): 사용자가 charger 를 빼는 시점의 신호 진동이 ON 트리거를
        # 발생시켰고 PENDING 정착 시 d_h1=-162 였는데 ON 흐름이 그대로 진행되어 LOW-POWER UPDATE 로
        # 흡수, 진짜 OFF 신호가 baseline 에 묻혀 charger 가 영영 OFF 못함. RF 결과를 폐기하고
        # OFF event 처리로 넘긴다 — _handle_device_off 가 active sig 와 매칭해서 OFF/partial-reject 결정.
        d_h1_check = float(win_feat.get("H1_60_mag_mean", 0.0)) - pre_h1
        d_irms_check = float(win_feat.get("Irms_adc_mean", 0.0)) - pre_irms
        if d_h1_check < -100.0:
            logging.info(
                f"[PENDING ON → OFF REROUTE] 정착 d_irms={d_irms_check:.1f}, d_h1={d_h1_check:.1f} 음수 → "
                f"transient ON, OFF pathway 로 위임"
            )
            self._handle_device_off(win_feat)
            return

        # v68: cond2 ON 트리거 시점 (first_feat) d_h1 보존. ID-STABLE 시점 d_h1 이 HP duty
        # noise 에 묻혀 작게 측정될 때, low_power_region 의 signal_candidate 결정에 cond2
        # 시점 값을 fallback 으로 사용. 실측 (2026-05-29 17:08:43~45): cleaner+microwave+
        # dryer active 중 사용자가 charger 꽂음. cond2 d_h1=334 (charger 신호 명확) →
        # ~3초 후 ID-STABLE d_h1=-38 (HP duty 가 baseline 끌어올림) → SIGNAL-WEAK → reject.
        try:
            self._current_cond2_d_h1 = None
            if pending and pending.get("first_feat"):
                self._current_cond2_d_h1 = float(
                    pending["first_feat"].get("H1_60_mag_mean", 0.0)
                ) - pre_h1
        except Exception:  # noqa: BLE001
            self._current_cond2_d_h1 = None

        device, conf, method, details = self._identify_device_stable(win_feat, pre_feat, pre_irms, pre_h1)

        d_irms = float(win_feat.get("Irms_adc_mean", 0.0)) - pre_irms
        d_h1 = float(win_feat.get("H1_60_mag_mean", 0.0)) - pre_h1
        d_pabs = float(win_feat.get("Pabs_mean_proxy_mean", win_feat.get("Pabs_mean_proxy", 0.0))) - float(pre_feat.get("Pabs_mean_proxy_mean", pre_feat.get("Pabs_mean_proxy", 0.0)))
        # v99: H5_300_mag delta. H5 는 extensive(가산) → OFF drop 으로 측정 가능. charger H5≈597
        # vs tv H5≈117 (5배차) 라 charger/tv OFF 매칭의 강한 단서 (절대 분리도 Cohen d=2.45 >
        # H1 의 1.60). 복제검증: score_for 에 추가 시 OFF 정확도 95.1→97.1%, 분리도 0.177→0.247.
        d_h5 = float(win_feat.get("H5_300_mag_mean", win_feat.get("H5_300_mag", 0.0))) - float(pre_feat.get("H5_300_mag_mean", pre_feat.get("H5_300_mag", 0.0)))

        if device is None:
            logging.warning(
                f"[DEVICE ON REJECT] unknown | reason={reason}, dI={d_irms:.1f}, dH1={d_h1:.1f}, dPabs={d_pabs:.1f}, details={details}"
            )
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        # v84: _identify_device_stable이 settling으로 판단 → 즉시 mode update 처리.
        # abs RF가 active HP를 강하게 지목한 소신호 케이스. 복잡한 is_mode_update 흐름을
        # 거치지 않고 baseline sync + cooldown 만 하고 반환.
        if method == "rf_abs_active_hp_settling":
            logging.info(
                f"[ON HP SETTLING] {device} abs RF settling 신호 → mode update "
                f"(d_irms={d_irms:.1f}, d_h1={d_h1:.1f})"
            )
            if device in HIGH_POWER_DEVICES:
                self.last_high_power_event_frame = self.frame_count
            self._sync_baseline_to(win_feat)
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        # v52d: LP RAMP CONTINUATION swap
        # 같은 TV (또는 charger) 의 ramp 가 분리되어 두 LP 가전으로 잘못 잡히는 케이스 보정.
        # 실측 (2026-05-27 15:01:39 → 15:01:48): 드라이기+청소기 active 중 TV 첫 등장이
        # dH1=1049 (boundary 1100 미달) 로 charger 오분류 (method=low_power_h1_over_rf_delta_hp).
        # 9초 뒤 TV ramp 가 계속 올라와 dH1=1452 의 두 번째 ON event 가 정확히 tv 로 분류.
        # 이때 charger 등록을 tv 로 swap 하지 않으면:
        #   1) tv 가 빈 socket 에 ghost 할당
        #   2) 사용자가 실제 charger 를 꽂아도 "charger already active" 로 ON SKIP
        #   3) OFF 시 라벨이 뒤집힌 채 cascade
        # swap 조건 (false positive 방지):
        #   - chosen 이 LP, 다른 LP 가 이미 active
        #   - 기존 등록 method 가 신호-only fallback (불확실 path) — 신뢰 path 면 진짜 다른 가전 가능성
        #   - 등록 후 elapsed ≤ 15 sec (wall-clock)
        if (device in LOW_POWER_DEVICES
                and device not in self.active_devices):
            other_lp = "tv" if device == "charger" else "charger"
            if other_lp in self.active_devices:
                old_sig = self.device_signatures.get(other_lp, {})
                old_method = str(old_sig.get("method", ""))
                old_wall = float(self.device_on_wallclock.get(other_lp, 0.0))
                elapsed = time.time() - old_wall if old_wall > 0 else float("inf")
                if (old_method in LP_RAMP_SWAP_OLD_METHODS
                        and elapsed <= LOW_POWER_RAMP_CONTINUATION_SECONDS):
                    old_socket_idx = self.active_devices.pop(other_lp)
                    self.active_devices[device] = old_socket_idx
                    for sk in self.sockets:
                        if sk.idx == old_socket_idx:
                            sk.device = device
                            sk.power_w = DEVICE_REAL_POWER_W.get(device, 0.0)
                            break
                    # 새 signature: old_sig + 이번 event delta = 같은 가전의 전체 ramp 누적
                    cum_d_irms = float(old_sig.get("delta_irms", 0.0)) + d_irms
                    cum_d_h1 = float(old_sig.get("delta_h1", 0.0)) + d_h1
                    cum_d_pabs = float(old_sig.get("delta_pabs", 0.0)) + d_pabs
                    cum_d_h5 = float(old_sig.get("delta_h5", 0.0)) + d_h5  # v99: H5 도 누적
                    cum_d_pf = (
                        float(old_sig.get("delta_pf", 0.0))
                        + float(win_feat.get("PF_proxy_mean", 0.0))
                        - float(pre_feat.get("PF_proxy_mean", 0.0))
                    )
                    self.device_signatures[device] = {
                        "delta_irms": cum_d_irms,
                        "delta_h1": cum_d_h1,
                        "delta_pabs": cum_d_pabs,
                        "delta_h5": cum_d_h5,
                        "delta_pf": cum_d_pf,
                        "method": method + "_lp_swap",
                    }
                    self.device_signatures.pop(other_lp, None)
                    self.device_on_frames[device] = self.device_on_frames.pop(other_lp, self.frame_count)
                    self.device_on_wallclock[device] = self.device_on_wallclock.pop(other_lp, time.time())
                    logging.info(
                        f"[LP RAMP CONTINUATION] {other_lp} → {device} label swap on Socket{old_socket_idx} "
                        f"(elapsed={elapsed:.1f}s, old_method={old_method}, "
                        f"cum_dH1={cum_d_h1:.1f}, cum_dI={cum_d_irms:.1f})"
                    )
                    self.event_history.append((self.frame_count, "RELABEL", f"{other_lp}->{device}"))
                    self._sync_baseline_to(win_feat)
                    self.event_cooldown = EVENT_COOLDOWN_FRAMES
                    return

        # v6: charger/tv는 켜진 뒤 H1이 천천히 올라가는 ramp가 길다.
        # 이걸 새 기기 ON으로 처리하면 TV/charger 중복 슬롯이 생기므로 low-power active label은 update로 흡수한다.
        #
        # v25 (2026-05-22): _is_mode_update 조건 추가.
        # 실측: charger 등록 후 사용자가 TV 를 꽂았는데 multi-device 합산 신호가 abs charger 0.65 로 보여
        #       chosen=charger 가 됐고, 이 분기가 _is_mode_update 검사 없이 "charger active + low-power 면
        #       무조건 흡수" 라서 TV 가 영영 등록 못 했다 (그 결과 마지막 TV OFF 가 OFF SKIP).
        #       sig 와 일치하는 작은 변화만 흡수하도록 _is_mode_update 조건 추가.
        #       (delta tv:0.40 가 정확한 단서였으나 abs 가 우선되는 별도 한계는 v26+ 에서 다룰 수 있음)
        if (device in self.active_devices and device in LOW_POWER_DEVICES
                and d_irms < LOW_POWER_DI_MAX and d_h1 < LOW_POWER_DH1_MAX
                and abs(d_pabs) < LOW_POWER_PABS_MAX
                and self._is_mode_update(device, d_irms, d_h1)):
            logging.info(f"[LOW-POWER UPDATE] {device} already active and matches sig (mode/ramp); absorb")
            self._sync_baseline_to(win_feat)
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        if device in self.active_devices and not self._is_mode_update(device, d_irms, d_h1):
            # 이미 active인 label로 나왔더라도 실제로 새 부하가 들어온 상황일 수 있다.
            # 1) charger/tv는 순서상 서로 이어서 들어오는 경우가 많으므로 H1 기준 alternate를 먼저 본다.
            alt = None

            # v52i: ALT LP RAMP CONTINUATION 가드 (elapsed 조건 제거).
            # v52g 는 wall-clock 15s 이내만 가드 발동했으나 실측 (2026-05-27 17:13:28) 에서
            # TV ramp 가 21s 까지 multi-stage 로 지속되어 가드 못 잡고 가짜 charger 등록 →
            # 진짜 충전기 ON SKIP → 충전기 뽑은 신호가 cleaner OFF 로 잘못 매칭 → tv 미인식 →
            # 드라이기 끄고서야 cleanup 으로 tv/charger 늦게 정리되는 cascade 폭발.
            #
            # 단순화 정책: chosen 이 이미 active 인 LP 가전 (tv 또는 charger) 이고 추가 event 의
            # d_h1 ≥ 1000 이면 elapsed 무관 보류.
            # 근거:
            #   - 진짜 다른 LP 가전이 새로 들어오는 경우 단독 신호 d_h1: charger ≈ 400~500.
            #     1000 이상은 거의 항상 같은 LP 의 multi-stage ramp 후반부.
            #   - 진짜 다른 LP 의 신호 영역 (d_h1 ≤ boundary 1100, 또는 d_h1 ≥ 1100 이지만
            #     range 가 진짜 LP 매치) 는 정상 등록 path 에서 별도 event 로 잡힘.
            #   - 가드 발동해도 baseline 동기화 안 함 → 진짜 다른 LP 가 들어오면 다음 ON event 가
            #     다시 트리거되어 정상 분류 가능.
            #
            # 부작용: charger active 중 RF 가 진짜 TV (d_h1 ≥ 1100) 를 charger 로 잘못 분류한
            # 케이스에 가드 발동해 TV 미등록. 그러나 RF 가 d_h1 ≥ 1000 영역에서 charger 분류할
            # 확률은 낮고 (실측 RF tv 정확도 70%+), 발생해도 다음 cycle 에 재시도 가능.
            if device in LOW_POWER_DEVICES and d_h1 >= 1000.0:
                lp_age = time.time() - float(self.device_on_wallclock.get(device, 0.0))
                logging.info(
                    f"[ALT LP-RAMP GUARD] {device} 이미 active + d_h1={d_h1:.1f} ≥ 1000 → "
                    f"multi-stage ramp 가능성, ALT/RANGE/ABS fallback 전부 보류 (등록 후 {lp_age:.1f}s, "
                    f"baseline 동기화 없이 cooldown)"
                )
                self.event_cooldown = max(2, EVENT_COOLDOWN_FRAMES // 2)
                return
            elif device == "charger" and "tv" not in self.active_devices and d_h1 >= 450.0:
                alt = "tv"
            elif device == "tv" and "charger" not in self.active_devices:
                # v52b: tv 가 이미 active 일 때, 두 번째 LP 가전은 charger 가 유일한 후보
                # (지원 라벨이 charger/tv 둘뿐이므로). CHARGER_TV_H1_BOUNDARY 는 charger vs
                # tv 모호 영역에서 신호로 구분하기 위한 임계지만, tv 가 이미 active 면
                # 무의미 — 두 번째 TV 는 없으므로 charger 가 정답.
                #
                # 실측 (2026-05-27 02:10:11): cleaner+dryer+tv active 중 사용자가 charger
                # 꽂음. cleaner duty-cycle UP-beat 가 charger ramp 와 겹쳐 dH1=1706.3 으로
                # boundary 1100 초과 → 기존 분기 실패. fallback 인 inactive range candidate
                # 도 dryer active 영향으로 range_score=1.115 → v45 strict 0.80 임계로 거절
                # → ON SKIP → charger 미등록 → 이후 baseline drift 가 TV OFF 오발동 유발.
                #
                # 두 조건 중 하나라도 만족하면 alt=charger 채택:
                #   - d_h1 ≤ boundary: 안전 영역 (기존 로직)
                #   - d_h1 > boundary AND 강한 LP 신호 (dI ≥ 20 AND dPabs ≥ 5000):
                #     HP duty-cycle 노이즈가 charger H1 위에 덧붙은 경우. v45 false positive
                #     (HP duty 변동 단독 false trigger) 는 dI < 20 또는 dPabs < 5000 으로
                #     걸러짐 — 진짜 charger 는 dI ≥ 30, dPabs ≥ 10000 정도로 강한 신호.
                if d_h1 <= CHARGER_TV_H1_BOUNDARY:
                    alt = "charger"
                elif d_irms >= 20.0 and d_pabs >= 5000.0:
                    alt = "charger"
                    logging.info(
                        f"[ALT CHARGER STRONG-SIG] tv 이미 active, d_h1={d_h1:.1f} > boundary={CHARGER_TV_H1_BOUNDARY:.0f} "
                        f"이지만 강한 LP 신호 (dI={d_irms:.1f}, dPabs={d_pabs:.1f}) → alt=charger 채택"
                    )

            # 2) 그 외에는 inactive range 후보를 보되, dryer는 진짜 dryer급일 때만 허용한다.
            if alt is None:
                alt = self._best_inactive_range_candidate(d_irms, d_h1, d_pabs)
                # v45: alt 가 range_score 1.15 통과해도 약한 매칭은 false positive 위험.
                # 실측 (2026-05-24 19:24:24): microwave duty 변동으로 cond2 ON false trigger,
                # chosen=tv (already active) → alt 검색에서 charger range_score=1.104 가 잡혀
                # 사용자가 안 꽂은 charger 가 잘못 등록. ON ACTIVE-LABEL FIX 분기는 strict 임계
                # (0.80) 적용 - 신호가 정말 alt 와 매칭될 때만 채택.
                if alt is not None:
                    alt_score = self._range_score(alt, d_irms, d_h1, d_pabs, use_p=True)
                    if alt_score > 0.80:
                        logging.info(
                            f"[ALT REJECT] {alt} range_score={alt_score:.2f} > 0.80 strict 임계 → "
                            f"신뢰 부족, alt 무효 (false positive 방지)"
                        )
                        alt = None

            # v22: range 가 미스여도 RF abs prob 의 inactive top 이 임계 이상이면 채택.
            # 실측 (2026-05-22 12:33:10): cleaner ramp 초입(dH1=2584)이 range 영역 측면에서는
            # dryer 영역과 겹쳐 alt=None 으로 떨어졌으나 RF abs 는 cleaner:0.54 같이 강한 단서를
            # 줬는데도 ON SKIP 으로 묻혔다. 그 결과 cleaner ramp 가 계속 올라오면서 baseline drift →
            # 8초 뒤 charger/tv 가 잘못 cascade OFF. 이 fallback 이 그 cascade 의 근본 원인이었다.
            if alt is None:
                alt = self._strong_inactive_abs_candidate(
                    win_feat, d_irms, d_h1, exclude=device, threshold=0.40
                )

            if alt and alt != device:
                logging.info(f"[ON ACTIVE-LABEL FIX] {device} already active -> use inactive candidate {alt}")
                device = alt
            else:
                logging.info(f"[ON SKIP] {device} already active and no reliable alternate; baseline not synced")
                # baseline을 새 부하에 동기화하면 이후 OFF가 전부 꼬인다.
                # 쿨다운만 짧게 걸고 baseline은 그대로 둔다.
                self.event_cooldown = max(2, EVENT_COOLDOWN_FRAMES // 2)
                return
        elif device in self.active_devices:
            # v40: HP active + low-power region 신호 → 새 low-power 기기 가능성 검증.
            # 실측 (2026-05-24 18:15:57): microwave active 중 사용자가 charger 꽂으니
            # d_irms=7.1, d_h1=681.7, chosen=microwave (rf_abs:0.98) → ON MODE UPDATE
            # 분기로 잘못 처리되어 charger 등록 실패. HP 가 dominant 라 RF_abs 가 microwave 만
            # 강하게 지목하기 때문. low-power region 신호이면 H1 boundary 로 charger/tv 우선.
            if (device in HIGH_POWER_DEVICES
                    and d_irms < LOW_POWER_DI_MAX and d_h1 < LOW_POWER_DH1_MAX
                    and abs(d_pabs) < LOW_POWER_PABS_MAX
                    and d_h1 >= 300.0):
                new_low_power = None
                if d_h1 <= CHARGER_TV_H1_BOUNDARY and "charger" not in self.active_devices:
                    new_low_power = "charger"
                elif d_h1 > CHARGER_TV_H1_BOUNDARY and "tv" not in self.active_devices:
                    new_low_power = "tv"
                elif "charger" not in self.active_devices:
                    new_low_power = "charger"
                elif "tv" not in self.active_devices:
                    new_low_power = "tv"

                if new_low_power is not None:
                    logging.info(
                        f"[ON HP-ACTIVE NEW LOW-POWER FIX] {device} active but low-power signal "
                        f"(d_irms={d_irms:.1f}, d_h1={d_h1:.1f}) → register {new_low_power}"
                    )
                    device = new_low_power
                    method = "hp_active_new_lp_fix"
                    # fall through 하여 등록 흐름 계속
                else:
                    logging.info(f"[ON MODE UPDATE] {device} already active, treat as mode/power update")
                    if device in HIGH_POWER_DEVICES:
                        self.last_high_power_event_frame = self.frame_count
                    self._sync_baseline_to(win_feat)
                    self.event_cooldown = EVENT_COOLDOWN_FRAMES
                    return
            else:
                # v80: HP active + HP 크기 신호 → mode update 전 inactive HP 후보 확인.
                # 실측 (2026-05-30 18:01): microwave active 중 cleaner 꽂으니 dI=109.4, dH1=5816.2
                # → RF chosen=microwave, _is_mode_update=True (5816 < 35% of microwave sig ~22000)
                # → elif → else 로 떨어져 MODE UPDATE 흡수 → cleaner 영영 미등록.
                # cleaner dI≈109, dH1≈5816 은 class_range (Irms 133-142, H1 6238-6557) 와 match.
                #
                # v80b: 신호가 LP 수준 (dI<45 AND dH1<2400) 이면 탐색 생략.
                # 실측 (2026-05-30 18:39): microwave 기동 직후 settling 신호 dI=28.6, dH1=1652.7
                # → charger range_score=1.030 에 걸려 잘못 등록. 진짜 새 HP 기기는 LP 크기보다 큰
                # 신호를 만들기 때문에 LP 임계 미만 신호는 mode update 로 처리한다.
                if (device in HIGH_POWER_DEVICES
                        and (d_irms >= LOW_POWER_DI_MAX or d_h1 >= LOW_POWER_DH1_MAX)):
                    hp_alt = self._best_inactive_range_candidate(d_irms, d_h1, d_pabs)
                    if hp_alt is not None:
                        logging.info(
                            f"[ON MODE-UPDATE → NEW HP] {device} active + _is_mode_update 이지만 "
                            f"inactive '{hp_alt}' range 매치 (dI={d_irms:.1f}, dH1={d_h1:.1f}) → register {hp_alt}"
                        )
                        device = hp_alt
                        method = "mode_update_new_hp"
                        # fall through to registration code below
                    else:
                        logging.info(f"[ON MODE UPDATE] {device} already active, treat as mode/power update")
                        self.last_high_power_event_frame = self.frame_count
                        self._sync_baseline_to(win_feat)
                        self.event_cooldown = EVENT_COOLDOWN_FRAMES
                        return
                else:
                    logging.info(f"[ON MODE UPDATE] {device} already active, treat as mode/power update")
                    self._sync_baseline_to(win_feat)
                    self.event_cooldown = EVENT_COOLDOWN_FRAMES
                    return

        target_sk = self._select_socket_for(device)
        if target_sk is None:
            logging.warning(f"[ON FAIL] {device} - no available socket")
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        self._socket_prior_state[target_sk.idx] = (target_sk.state, target_sk.device)
        power_w = DEVICE_REAL_POWER_W.get(device, 0.0)
        target_sk.assign_device(device, power_w)
        self.active_devices[device] = target_sk.idx

        # v29: 이전 OFF 된 같은 라벨의 백업 sig 가 더 크면 그것 사용.
        # 실측 (2026-05-22 17:27:54): cleaner + dryer active 중 charger 재등록 시 측정 d_h1=430
        # 이지만 Phase 1 의 단독 charger sig 는 d_h1=978 (백업됨). 측정값으로 덮어쓰면 후속 OFF
        # cascade match 가 sig 영역 벗어나 다른 기기가 잘못 force OFF.
        cached_sig = self.device_signatures_history.get(device)
        # v34: delta_pf 도 함께 저장 (charger PF=0.17~0.34, tv PF=0.42~0.50 의 명확한 차이를
        # OFF 매칭에 활용). dH1 만으로는 charger/tv 구별 못하는 ambiguous 케이스 해결.
        d_pf = float(win_feat.get("PF_proxy_mean", 0.0)) - float(pre_feat.get("PF_proxy_mean", 0.0))

        if cached_sig is not None and abs(float(cached_sig.get("delta_h1", 0.0))) > abs(d_h1):
            logging.info(
                f"[SIG HISTORY] {device} new dH1={d_h1:.1f} smaller than cached "
                f"{cached_sig.get('delta_h1', 0.0):.1f} (dominance suspected); keep cached sig"
            )
            self.device_signatures[device] = dict(cached_sig)
        else:
            self.device_signatures[device] = {
                "delta_irms": d_irms,
                "delta_h1": d_h1,
                "delta_pabs": d_pabs,
                "delta_h5": d_h5,  # v99: charger/tv OFF 매칭 단서 (extensive, 5배차)
                "delta_pf": d_pf,
                "method": method,
            }
        self.device_on_frames[device] = self.frame_count
        self.device_on_wallclock[device] = time.time()

        logging.info(
            f"[DEVICE ON] Socket{target_sk.idx} <- {device} ({power_w:.0f}W, conf={conf:.2f}, method={method}, "
            f"d_irms={d_irms:.1f}, d_h1={d_h1:.1f}, d_pabs={d_pabs:.1f}, details={details})"
        )

        self.event_history.append((self.frame_count, "ON", device))
        if device in HIGH_POWER_DEVICES:
            self.last_high_power_event_frame = self.frame_count
        self._sync_baseline_to(win_feat)
        self._pending_off_drop = False  # v12: 새 ON event → 누적 대기 종료
        self._consecutive_partial_rejects = 0  # v18
        self._cascade_drop_history = []  # v30
        self.event_cooldown = EVENT_COOLDOWN_FRAMES
        self.reclassify_countdown = RECLASSIFY_DELAY
        self.pre_event_baseline_feat = pre_feat
        self.pre_event_baseline_irms = pre_irms
        self.pre_event_baseline_h1 = pre_h1

    def _select_socket_for(self, device):
        for sk in self.sockets:
            if sk.state == "EMPTY":
                return sk
        for sk in self.sockets:
            if sk.state == "DEVICE_OFF" and sk.device == device:
                return sk
        for sk in self.sockets:
            if sk.state == "DEVICE_OFF":
                logging.info(f"[SOCKET RECYCLE] Socket{sk.idx} ({sk.device}) -> {device}")
                return sk
        return None

    def _is_mode_update(self, device, d_irms, d_h1):
        # 같은 기기 label이 active인데 출력 변화가 그 기기 크기의 일부이면 모드 변경으로 본다.
        sig = self.device_signatures.get(device, {})
        sig_h1 = abs(float(sig.get("delta_h1", 0.0)))
        sig_i = abs(float(sig.get("delta_irms", 0.0)))
        if sig_h1 <= 0 and sig_i <= 0:
            return False
        # v26: d_h1 이 명백히 음수 (OFF 방향) 이면 mode_update 가 아니라 OFF event.
        # 실측 (2026-05-22 16:11:32): charger 빼는 transient 의 PENDING 정착이 d_h1=-162 였는데
        # abs 비교로 mode_update=True 가 되어 OFF 신호가 baseline 에 흡수되었다.
        if d_h1 < -100.0:
            return False
        # 드라이기 모드 변경 방어
        if device == "dryer" and abs(d_h1) > 1500:
            return True
        return abs(d_h1) < max(sig_h1 * 0.35, 300.0) and abs(d_irms) < max(sig_i * 0.35, 10.0)

    # ------------------------------------------------------------------
    # Device identification
    # ------------------------------------------------------------------
    def _identify_device_stable(self, win_feat, pre_feat, pre_irms, pre_h1):
        classes = list(self.model.classes_)

        X_abs = pd.DataFrame([win_feat])[self.feature_names].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        probs_abs = self.model.predict_proba(X_abs)[0]
        abs_pred = str(classes[int(np.argmax(probs_abs))])
        abs_conf = float(max(probs_abs))
        prob_abs = {str(c): float(p) for c, p in zip(classes, probs_abs)}

        delta_feat = {}
        for k in self.feature_names:
            v = float(win_feat.get(k, 0.0)) - float(pre_feat.get(k, 0.0))
            # 모델 feature 대부분은 magnitude 계열이므로 ON 후보는 음수를 0으로 클램프
            delta_feat[k] = max(0.0, v)

        X_delta = pd.DataFrame([delta_feat])[self.feature_names].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        probs_delta = self.model.predict_proba(X_delta)[0]
        delta_pred = str(classes[int(np.argmax(probs_delta))])
        delta_conf = float(max(probs_delta))
        prob_delta = {str(c): float(p) for c, p in zip(classes, probs_delta)}

        d_irms = float(win_feat.get("Irms_adc_mean", 0.0)) - pre_irms
        d_h1 = float(win_feat.get("H1_60_mag_mean", 0.0)) - pre_h1
        d_pabs = float(win_feat.get("Pabs_mean_proxy_mean", win_feat.get("Pabs_mean_proxy", 0.0))) - float(pre_feat.get("Pabs_mean_proxy_mean", pre_feat.get("Pabs_mean_proxy", 0.0)))

        range_pred, range_score, score_map = self._range_match(d_irms, d_h1, d_pabs)

        # RF 결과 sanity
        delta_ok = self._candidate_plausible(delta_pred, d_irms, d_h1, d_pabs)
        abs_ok = self._candidate_plausible(abs_pred, float(win_feat.get("Irms_adc_mean", 0.0)), float(win_feat.get("H1_60_mag_mean", 0.0)), float(win_feat.get("Pabs_mean_proxy_mean", 0.0)), absolute=True)

        # v6 핵심 원칙:
        # 1) low-power(charger/tv)는 RF_delta가 tv로 쏠려도 순서/크기 기반으로 먼저 분리한다.
        #    현재 로그에서 charger가 tv로, TV가 charger로 뒤집힌 원인은 이 구간을 RF_delta에 맡겼기 때문이다.
        # 2) cleaner는 RF_delta가 cleaner라고 말하는 구간을 dryer로 덮지 않는다.
        # 3) microwave는 RF_abs가 매우 강하게 맞으므로 최우선으로 보호한다.
        # 4) dryer는 정말 큰 dI/dH1이 있을 때만 허용한다.
        low_power_region = (d_irms < LOW_POWER_DI_MAX
                            and d_h1 < LOW_POWER_DH1_MAX
                            and abs(d_pabs) < LOW_POWER_PABS_MAX)
        cleaner_like = (CLEANER_DI_MIN <= d_irms <= CLEANER_DI_MAX
                        and CLEANER_DH1_MIN <= d_h1 <= CLEANER_DH1_MAX)
        dryer_strong = (d_irms >= DRYER_STRONG_DI or d_h1 >= DRYER_STRONG_DH1)
        microwave_strong = (d_irms >= MICROWAVE_DI_MIN and d_h1 >= MICROWAVE_DH1_MIN)
        # v32: microwave ramp 초기 영역. abs_conf 가 강하면 (>=0.65) 이 영역도 microwave 로 인정.
        # 실측 (2026-05-22 18:38:34): microwave 신호가 dI=168, dH1=7840 으로 cleaner_like 영역에
        # 떨어졌는데 RF abs=microwave:0.68 강한 단서. microwave_strong (DI>=200, DH1>=12000) 미달로
        # cleaner 로 잘못 분류 → range_fallback path 진입. microwave_likely 로 ramp 초기 영역 cover.
        microwave_likely = (d_irms >= 100.0 and d_h1 >= 3000.0)

        # === v24: 행동지침 (active 순서) 의존 제거 ===
        # 이전 코드는 "charger 가 아직 active 가 아니면 무조건 charger 우선,
        # tv 가 아직 active 가 아니면 무조건 tv" 식으로 행동지침 (charger → tv → ...)
        # 가정에 의존했다. 사용자가 임의 순서로 꽂는 실 시나리오에서는 가정이 깨져
        # 명백한 오분류 (실측 2026-05-22 14:03: charger 꽂았는데 tv 등록, tv 꽂았는데
        # charger 등록) 가 발생했다.
        #
        # 새 정책: active_devices 상태 무관. RF (abs/delta) + 신호 (H1 boundary) 의
        # cross-check 만으로 charger/tv 결정.
        #   1) RF best 와 신호 후보 일치 → 그 후보 (강한 신뢰)
        #   2) RF best conf ≥ 0.70 → RF 채택 (모델이 매우 확신)
        #   3) 모순 + RF conf < 0.70 → 신호 우선 (H1 boundary 가 학습 데이터에 직접 근거)
        # v85: low_power_region 진입 *전에* settling guard.
        # 실측 (2026-05-30 21:23:32): microwave active 중 작은 신호 (dI=12.9, dH1=159.2)
        # 발생 → low_power_region 진입 → H1 boundary (1100) 미달로 charger 잘못 등록.
        # abs RF microwave:1.00 인데 v84 분기가 low_power_region 다음에 위치해서 도달 못 함.
        # 해결: low_power_region 보다 먼저 체크. active HP 가 abs RF 를 압도하고 신호가
        # LP sig 보다 작은 settling 크기면 → settling 처리. _register_device_from_stable_window
        # 의 method=="rf_abs_active_hp_settling" 분기가 baseline sync + cooldown 으로 흡수.
        # 임계 dI<17, dH1<300: 진짜 charger 첫 ramp (dI≈18, dH1≈400~500) 보다 보수적으로 작게.
        v85_active_hp_settling = (
            low_power_region
            and abs_pred in HIGH_POWER_DEVICES
            and abs_conf >= 0.90
            and abs_pred in self.active_devices
            and d_irms < 17.0
            and d_h1 < 300.0
        )
        if v85_active_hp_settling:
            chosen = abs_pred
            conf = abs_conf
            method = "rf_abs_active_hp_settling"
            logging.info(
                f"[LOW-POWER ACTIVE-HP-SETTLING v85] active {abs_pred} "
                f"(abs RF {abs_conf:.2f}) 중 작은 신호 (dI={d_irms:.1f}, dH1={d_h1:.1f}) "
                f"→ LP 분기 우회, HP settling 으로 흡수 (charger 가짜 ON 방지)"
            )
        elif low_power_region:
            # v55: d_h1 음수 / 매우 작은 양수 → 신호 단서 무효.
            # 실측 (2026-05-28 17:01:26): dryer+cleaner active 중 사용자가 TV 꽂음.
            # TV ramp 가 HP 자연 변동에 가려져 d_h1=-96.8 (음수) 측정. boundary 1100 비교는
            # 무의미한데 (charger 든 tv 든 둘 다 양의 H1 ramp 가전) 코드가 d_h1 < 1100 →
            # charger 영역으로 잘못 분류 → RF delta tv:0.71 무시 → signal=charger 채택.
            # 결과: TV 가 charger 라벨로 등록되어 이후 모든 OFF/매핑 cascade 오류.
            # charger H1 학습 분포: p10=358. d_h1 < SIGNAL_MIN_DH1 (100) 면 charger/tv 어느
            # 쪽 ramp 도 아닌 노이즈 영역 → RF 단독으로 결정.
            SIGNAL_MIN_DH1 = 100.0
            # v68: cond2 시점 d_h1 fallback. ID-STABLE 시점 측정값이 HP duty noise 로 묻혀
            # 작아도, cond2 트리거 시점 (3초 전) 의 값이 강하면 그 값으로 signal_candidate
            # 결정. RF 추론은 win_feat 그대로 (불변) → 신호 vs RF cross-check 로 안전.
            effective_d_h1 = d_h1
            cond2_d_h1 = getattr(self, "_current_cond2_d_h1", None)
            if (cond2_d_h1 is not None
                    and d_h1 < SIGNAL_MIN_DH1
                    and cond2_d_h1 >= SIGNAL_MIN_DH1):
                logging.info(
                    f"[COND2-DH1 RESTORE] ID-STABLE d_h1={d_h1:.1f} < {SIGNAL_MIN_DH1:.0f} "
                    f"(HP duty noise 추정), cond2 시점 d_h1={cond2_d_h1:.1f} 사용 → "
                    f"signal_candidate 결정에만 적용"
                )
                effective_d_h1 = cond2_d_h1
            if effective_d_h1 < SIGNAL_MIN_DH1:
                signal_candidate = None
            else:
                signal_candidate = "tv" if effective_d_h1 >= CHARGER_TV_H1_BOUNDARY else "charger"

            rf_lp_candidates = []
            if abs_pred in LOW_POWER_DEVICES:
                rf_lp_candidates.append((abs_pred, abs_conf, "abs"))
            if delta_pred in LOW_POWER_DEVICES:
                rf_lp_candidates.append((delta_pred, delta_conf, "delta"))

            if rf_lp_candidates:
                rf_lp_candidates.sort(key=lambda x: -x[1])
                rf_best, rf_best_conf, rf_src = rf_lp_candidates[0]

                # v55: signal_candidate 없으면 신호 vs RF cross-check 불가 → RF 단독.
                # 단 conf 가 낮으면 (< 0.45) 노이즈 영역에서의 RF 분포 자체도 신뢰 낮으므로
                # 보류 (chosen=None → 일반 흐름에서 등록 skip 처리).
                if signal_candidate is None:
                    if rf_best_conf >= 0.45:
                        chosen = rf_best
                        conf = rf_best_conf
                        method = f"low_power_rf_only_signal_weak_{rf_src}"
                        logging.info(
                            f"[LOW-POWER SIGNAL-WEAK] d_h1={d_h1:.1f} < {SIGNAL_MIN_DH1:.0f} "
                            f"(신호 단서 무효) → RF {rf_src} 단독 채택: {rf_best} ({rf_best_conf:.2f})"
                        )
                    else:
                        chosen = None
                        conf = 0.0
                        method = "low_power_signal_weak_skip"
                        logging.info(
                            f"[LOW-POWER SIGNAL-WEAK SKIP] d_h1={d_h1:.1f} 신호 단서 무효 "
                            f"AND RF best conf={rf_best_conf:.2f} 낮음 → 보류"
                        )
                # v41: dominant HP active 중에는 RF 신뢰도 낮음 → 정책 2번 임계 강화.
                # 실측 (2026-05-24 18:35:16): microwave active 중 charger 연결 시 신호=charger
                # (d_h1=616 < 1100) 였으나 RF delta tv:0.76 > 0.70 임계로 tv 잘못 채택.
                # microwave 같은 dominant HP 는 RF abs 를 압도해서 (microwave:0.997) 작은
                # low-power 신호의 prob 분포가 왜곡됨. 0.90 임계로 신호 우선 fallback.
                has_dominant_hp_rf = any(
                    abs(float(self.device_signatures.get(d, {}).get("delta_h1", 0.0))) > 5000.0
                    for d in self.active_devices
                    if d in HIGH_POWER_DEVICES
                )
                high_conf_threshold = 0.90 if has_dominant_hp_rf else 0.70
                # v51: signal=charger (d_h1 < boundary, "모호 영역") 인 경우 RF tv 임계 0.80 으로 완화.
                # 실측 (2026-05-25 01:39:53): dryer active 중 TV 연결 → TV ramp 초기 d_h1=670 으로
                # charger 영역 (boundary 1100 미만) 에 떨어짐. RF delta tv:0.86 강한 단서지만 v41
                # 임계 0.90 미달로 signal=charger 잘못 채택. 0.80 으로 낮추면 진짜 TV ramp 잡고
                # v41 실측 케이스 (실제 charger 연결, RF tv:0.76) 는 여전히 signal=charger 유지.
                # signal=tv (d_h1 ≥ 1100) 는 그 자체로 강한 신호라 임계 0.90 유지.
                if (signal_candidate == "charger"
                        and has_dominant_hp_rf
                        and rf_best == "tv"):
                    high_conf_threshold = 0.80
                if rf_best == signal_candidate:
                    chosen = rf_best
                    conf = max(rf_best_conf, 0.65)
                    method = f"low_power_rf_signal_match_{rf_src}"
                elif rf_best_conf >= high_conf_threshold:
                    chosen = rf_best
                    conf = rf_best_conf
                    method = f"low_power_rf_high_conf_{rf_src}"
                else:
                    chosen = signal_candidate
                    conf = max(rf_best_conf, 0.50)
                    method = f"low_power_h1_over_rf_{rf_src}" + ("_hp" if has_dominant_hp_rf else "")
            else:
                # RF 가 둘 다 low-power 가 아니지만 low_power_region 진입한 경우 (드묾) → 신호로 결정
                chosen = signal_candidate
                conf = max(abs_conf, delta_conf, 0.45)
                method = "low_power_h1_only"

        # microwave는 RF_abs가 강하면 range가 dryer라도 그대로 유지.
        # v32: abs_conf 0.70 → 0.65 완화 + microwave_likely (ramp 초기 영역) 허용.
        elif abs_pred == "microwave" and abs_conf >= 0.65 and (microwave_strong or microwave_likely):
            chosen = "microwave"
            conf = abs_conf
            method = "rf_abs_microwave_priority"

        # cleaner 보호: 이번 로그의 cleaner 구간은 delta cleaner=0.56, dI≈117, dH1≈7706이었다.
        # v52c: dryer/microwave active 중 cleaner ON 검출 보강.
        # 실측 (2026-05-27 02:42:13): dryer active 중 사용자가 cleaner 꽂음.
        # dI=122.9, dH1=6025.3, dPabs=70884.5 → cleaner_like ✓ + range cleaner=0.205
        # (정밀 매치, dryer range 가 너무 넓어 dryer=0.0 도 fit 하지만 비특이적).
        # probs_delta cleaner=0.387 / dryer=0.577 — 모델이 dryer ramp 과 confused 라
        # delta_pred=dryer (TOP), cleaner 가 두 번째. 기존 분기 (delta_pred==cleaner AND
        # conf≥0.40) 통과 못하고 fall-through 한 rf_delta 가 dryer 채택 → 이미 active
        # 인 dryer 의 mode update 로 흡수 → cleaner 등록 실패.
        #
        # 추가 조건: cleaner_like 영역 + cleaner prob ≥ 0.30 (의미 있는 RF 단서)
        # + range cleaner ≤ 0.50 (cleaner 분포 영역에 정밀 위치) + cleaner 미등록 +
        # d_pabs ≥ 5000 (HP mode noise 가 아닌 진짜 신규 부하). 이 조합은 dryer
        # 단순 ramp/mode 와 명확히 구분되어 false positive 위험 낮음.
        elif cleaner_like and (
                (delta_pred == "cleaner" and delta_conf >= 0.40)
                or (abs_pred == "cleaner" and abs_conf >= 0.30)
                or (prob_delta.get("cleaner", 0.0) >= 0.30
                    and score_map.get("cleaner", float("inf")) <= 0.50
                    and "cleaner" not in self.active_devices
                    and d_pabs >= 5000.0)
                # v52e: dryer/microwave 가 sig_h1 ≥ 10000 으로 dominant active 중이면
                # RF abs 가 dominant HP 에 쏠리고 (실측 dryer:0.95), cleaner range 도
                # 측정값이 dryer 분포에 흡수돼 cleaner range_score > 0.50 으로 깎임.
                # 그 결과 prob/range 두 임계 다 미달 → v52c 분기 못 통과 → rf_delta dryer
                # 채택 → ON MODE UPDATE 흡수 → cleaner 영영 미등록 → orchestrator socket
                # 매핑이 한 칸씩 밀리는 cascade 발생.
                # 실측 (2026-05-27 15:33:36): dryer (sig=35531) active 중 cleaner 꽂음.
                # dI=79.5, dH1=4479.7, dPabs=40648 → cleaner_like 정확히 ✓.
                # prob_delta cleaner=0.11, range cleaner=1.66 → 두 임계 모두 미달.
                # 안전망: cleaner_like + d_pabs ≥ 30000 + cleaner 미등록 + 다른 HP 가
                # sig_h1 ≥ 10000 로 dominant → cleaner 채택. dryer mode/duty 변동이
                # dPabs 30000 까지 가는 케이스 드물어 false positive 위험 낮음.
                or (
                    "cleaner" not in self.active_devices
                    and d_pabs >= 30000.0
                    and any(
                        d != "cleaner"
                        and d in HIGH_POWER_DEVICES
                        and abs(float(self.device_signatures.get(d, {}).get("delta_h1", 0.0))) >= 10000.0
                        for d in self.active_devices
                    )
                )
            ):
            chosen = "cleaner"
            conf = max(delta_conf if delta_pred == "cleaner" else 0.0,
                       abs_conf if abs_pred == "cleaner" else 0.0,
                       prob_delta.get("cleaner", 0.0),
                       0.55)
            method = "cleaner_delta_abs_priority"

        # dryer는 강한 dryer 조건에서만 허용. cleaner_like 영역은 위에서 먼저 먹는다.
        elif dryer_strong and ((delta_pred == "dryer" and delta_conf >= 0.45)
                               or (abs_pred == "dryer" and abs_conf >= 0.35)):
            chosen = "dryer"
            conf = max(delta_conf if delta_pred == "dryer" else 0.0,
                       abs_conf if abs_pred == "dryer" else 0.0,
                       0.55)
            method = "dryer_strong_guarded"

        # v84: abs RF가 이미 active인 HP 기기를 강하게(conf≥0.90) 지목하는데
        # dryer_strong/cleaner_like 조건 미달이면 delta RF의 HP 결과를 무시하고 settling으로 처리.
        # 실측 (2026-05-30 19:49:43): microwave 등록 5초 후 settling 신호 (dI=48.4, dH1=2529.1)
        # abs RF: microwave:1.00 → (이 분기 없으면) delta RF: dryer:0.69 → dryer 잘못 등록.
        # active HP가 abs RF를 지배할 때 소신호는 settling이므로 active HP의 mode update로 처리.
        elif (abs_pred in HIGH_POWER_DEVICES
              and abs_conf >= 0.90
              and abs_pred in self.active_devices
              and not dryer_strong
              and not cleaner_like):
            chosen = abs_pred
            conf = abs_conf
            method = "rf_abs_active_hp_settling"

        # 그 외 RF_abs/RF_delta는 plausible일 때만 사용
        elif delta_ok and delta_conf >= RF_CONFIDENCE_THRESHOLD:
            chosen = delta_pred
            conf = delta_conf
            method = "rf_delta"
        elif abs_ok and abs_conf >= RF_CONFIDENCE_THRESHOLD:
            chosen = abs_pred
            conf = abs_conf
            method = "rf_abs"
        else:
            # 마지막 fallback: dryer range는 넓어서 기본적으로 제외.
            range_candidate = range_pred
            if range_candidate == "dryer" and not dryer_strong:
                range_candidate = self._best_non_dryer_range_candidate(d_irms, d_h1, d_pabs)

            if range_candidate is not None and range_candidate != "dryer" and range_score <= RANGE_OK_SCORE:
                chosen = range_candidate
                conf = max(0.40, 1.0 - min(range_score, 1.0) * 0.4)
                method = "range_fallback_no_dryer"
            else:
                # 정말 애매하면 RF_abs를 우선하되, dryer는 strong 조건 없으면 금지
                cand = abs_pred if abs_conf >= delta_conf else delta_pred
                if cand == "dryer" and not dryer_strong:
                    cand = self._low_power_h1_choice(d_h1) or self._best_non_dryer_range_candidate(d_irms, d_h1, d_pabs) or "charger"
                chosen = cand
                conf = max(abs_conf, delta_conf, 0.35)
                method = "low_conf_best_effort_guarded_v6"

        details = {
            "abs": f"{abs_pred}:{abs_conf:.2f}",
            "delta": f"{delta_pred}:{delta_conf:.2f}",
            "range": f"{range_pred}:{range_score:.2f}",
            "dI": round(d_irms, 1),
            "dH1": round(d_h1, 1),
            "dPabs": round(d_pabs, 1),
        }
        # v69: LP 디바이스 (charger/tv) 선택 시 dI/dH1 부호 모순 검증.
        # 실측 (2026-05-29 18:18:53): 사용자 cleaner ON 의도였지만 ID-STABLE 측정 dI=-2.4
        # (음수), dH1=162.8 (양수). RF tv=0.68 + signal=charger (dH1<1100) cross-check 로
        # chosen=charger 결정되어 잘못 등록 (실제는 dryer+microwave duty noise + cleaner
        # ramp 초기의 baseline drift). 진짜 LP ON 이면 dI/dH1 모두 양수 (ramp up signal).
        # 부호 모순 (dI<0 AND dH1>0) 은 LP ON 아닌 노이즈 / baseline drift 잔향으로 보고
        # reject. cleaner_like 영역이나 dryer_strong 같은 HP 분기에는 영향 없음.
        if chosen in LOW_POWER_DEVICES and d_irms < 0 and d_h1 > 0:
            logging.info(
                f"[LP SIGN MISMATCH] chosen={chosen} but dI={d_irms:.1f} (음수) AND "
                f"dH1={d_h1:.1f} (양수) → LP ON ramp 아닌 노이즈 추정, reject"
            )
            chosen = None
            conf = 0.0
            method = "lp_sign_mismatch_reject"

        # v73: LP 디바이스 chosen 시 dI/dH1 절대값 magnitude 검증.
        # 실측 (2026-05-29 20:31:49): 사용자가 S3 을 PENDING 으로 켠 직후 (아직 충전기 미연결)
        # baseline noise (d_irms=3.2, d_h1=33) + microwave duty 변동이 cond2 ON 임계 넘어
        # PENDING ON 트리거 → RF probs (charger 0.27, tv 0.65) cross-check 로 chosen=charger.
        # only-candidate 로 S3 에 가짜 charger 등록 → 사용자 보고 "안 꽂았는데 charger_on".
        # 진짜 LP ON 은 dI 5+ / dH1 100+ 이상 (charger sig 18/700, tv sig 30/1400 정도).
        # 둘 다 noise floor 이하면 baseline 흔들림으로 보고 reject.
        LP_MIN_DI_ABS = 5.0
        LP_MIN_DH1_ABS = 100.0
        if (chosen in LOW_POWER_DEVICES
                and abs(d_irms) < LP_MIN_DI_ABS
                and abs(d_h1) < LP_MIN_DH1_ABS):
            logging.info(
                f"[LP NOISE SKIP] chosen={chosen} but |dI|={abs(d_irms):.1f} < "
                f"{LP_MIN_DI_ABS:.0f} AND |dH1|={abs(d_h1):.0f} < {LP_MIN_DH1_ABS:.0f} → "
                f"baseline noise 영역, reject"
            )
            chosen = None
            conf = 0.0
            method = "lp_noise_skip"

        logging.info(f"[ID-STABLE] chosen={chosen} conf={conf:.2f} method={method} details={details}")
        logging.info(f"[ID-STABLE] probs_abs={self._round_probs(prob_abs)}")
        logging.info(f"[ID-STABLE] probs_delta={self._round_probs(prob_delta)}")
        logging.info(f"[ID-STABLE] range_scores={self._round_probs(score_map)}")

        return chosen, conf, method, details

    def _round_probs(self, d):
        return {k: round(float(v), 3) for k, v in sorted(d.items(), key=lambda kv: str(kv[0]))}

    def _low_power_h1_choice(self, d_h1):
        if d_h1 < H1_DEVICE_MIN:
            return None
        if d_h1 < CHARGER_TV_H1_BOUNDARY:
            return "charger"
        if d_h1 < CHARGER_TV_H1_CORRECTION_MAX:
            return "tv"
        return None

    def _candidate_plausible(self, dev, irms, h1, pabs, absolute=False):
        if dev not in self.class_ranges:
            return False
        score = self._range_score(dev, irms, h1, pabs, use_p=not absolute)
        # low-power 후보가 고H1/high-power 영역에 들어오면 강하게 reject
        r = self.class_ranges.get(dev, {})
        h1_hi = float(r.get("H1_60_mag_p90", 1e9))
        i_hi = float(r.get("Irms_adc_p90", 1e9))
        if dev in LOW_POWER_DEVICES:
            if h1 > h1_hi * (1.0 + RANGE_MARGIN) and h1 > 2200:
                return False
            if irms > i_hi * 2.0 and h1 > 2200:
                return False
        return score <= RANGE_OK_SCORE * (1.35 if absolute else 1.0)

    def _range_match(self, d_irms, d_h1, d_pabs):
        best_dev = None
        best_score = float("inf")
        scores = {}
        for dev in self.class_ranges:
            score = self._range_score(dev, d_irms, d_h1, d_pabs, use_p=True)
            scores[dev] = score
            if score < best_score:
                best_score = score
                best_dev = dev
        return best_dev, best_score, scores

    def _range_score(self, dev, irms, h1, pabs=0.0, use_p=True):
        r = self.class_ranges.get(dev, {})

        def dist_to_range(x, lo, hi):
            lo = float(lo); hi = float(hi)
            if hi < lo:
                hi = lo
            width = max(hi - lo, hi * 0.20, 1.0)
            if lo <= x <= hi:
                return 0.0
            if x < lo:
                return (lo - x) / width
            return (x - hi) / width

        i_score = dist_to_range(irms, r.get("Irms_adc_p10", 0.0), r.get("Irms_adc_p90", 1e9))
        h_score = dist_to_range(h1, r.get("H1_60_mag_p10", 0.0), r.get("H1_60_mag_p90", 1e9))
        score = 0.45 * i_score + 0.55 * h_score

        if use_p and "P_proxy_p10" in r:
            # P_proxy는 부호/위상 영향이 있으므로 보조 가중치만 준다.
            p_score = dist_to_range(abs(pabs), abs(float(r.get("P_proxy_p10", 0.0))), abs(float(r.get("P_proxy_p90", 1e9))))
            score = 0.35 * i_score + 0.45 * h_score + 0.20 * p_score
        return float(score)

    def _best_non_dryer_range_candidate(self, d_irms, d_h1, d_pabs):
        best = None
        best_score = float("inf")
        for dev in self.class_ranges:
            if dev == "dryer":
                continue
            score = self._range_score(dev, d_irms, d_h1, d_pabs, use_p=True)
            if score < best_score:
                best_score = score
                best = dev
        if best is not None and best_score <= RANGE_OK_SCORE:
            return best
        return None

    def _best_inactive_range_candidate(self, d_irms, d_h1, d_pabs):
        best = None
        best_score = float("inf")
        dryer_like = (d_h1 >= 3000.0 or d_irms >= 80.0)
        for dev in self.class_ranges:
            if dev in self.active_devices:
                continue
            if dev == "dryer" and not dryer_like:
                continue
            score = self._range_score(dev, d_irms, d_h1, d_pabs, use_p=True)
            if score < best_score:
                best_score = score
                best = dev
        if best is not None and best_score <= RANGE_OK_SCORE:
            return best
        return None

    def _strong_inactive_abs_candidate(self, win_feat, d_irms, d_h1, exclude=None, threshold=0.40):
        """RF abs probs 의 inactive top 후보가 임계 이상이면 반환.

        ON SKIP 직전 fallback 으로 호출된다. range_score 가 미스여도 RF abs 가 inactive
        후보를 강하게 가리키면 새 가전 등록을 시도한다 (대표적 케이스: cleaner ramp 초입의
        dI/dH1 이 cleaner_like 영역 진입 전이지만 RF abs 는 이미 cleaner 를 강하게 지목).

        dryer 만 strong 조건(큰 dI 또는 dH1)이 같이 있을 때만 허용한다 - dryer range 는
        가장 넓어서 prob 만으로 채택하면 다른 가전을 dryer 로 오등록할 위험.
        """
        try:
            X = pd.DataFrame([win_feat])[self.feature_names].replace([np.inf, -np.inf], np.nan).fillna(0.0)
            probs = self.model.predict_proba(X)[0]
        except Exception as e:
            logging.warning(f"[ABS-FALLBACK] predict_proba 실패: {e}")
            return None

        classes = list(self.model.classes_)
        dryer_strong = (d_irms >= DRYER_STRONG_DI or d_h1 >= DRYER_STRONG_DH1)
        # v32: high-power 후보는 신호 크기 검증. 작은 신호에 큰 sig 후보가 매칭되어
        # microwave/cleaner 가 false positive 로 채택되는 케이스 방어.
        # 실측 (2026-05-22 18:37:42): charger ramp 의 d_h1=442 / dI=11 에서 ABS-FALLBACK 가
        # inactive top=microwave:0.44 채택 → microwave 잘못 등록 (즉시 OFF 되긴 함).
        microwave_likely = (d_irms >= 100.0 and d_h1 >= 3000.0)
        cleaner_likely = (d_irms >= 50.0 and d_h1 >= 3000.0)
        candidates = []
        for cls, p in zip(classes, probs):
            if cls == exclude or cls in self.active_devices:
                continue
            if cls == "dryer" and not dryer_strong:
                continue
            if cls == "microwave" and not microwave_likely:
                continue
            if cls == "cleaner" and not cleaner_likely:
                continue
            candidates.append((cls, float(p)))

        if not candidates:
            return None
        candidates.sort(key=lambda x: -x[1])
        top_dev, top_p = candidates[0]
        if top_p >= threshold:
            logging.info(f"[ABS-FALLBACK] inactive top={top_dev}:{top_p:.2f} (threshold={threshold:.2f})")
            return top_dev
        return None

    # ------------------------------------------------------------------
    # OFF handling
    # ------------------------------------------------------------------
    def _handle_device_off(self, win_feat):
        if not self.active_devices:
            d_irms = float(win_feat.get("Irms_adc_mean", 0.0)) - self.baseline_irms
            d_h1 = float(win_feat.get("H1_60_mag_mean", 0.0)) - self.baseline_h1
            logging.warning(
                f"[OFF SKIP] no active devices d_irms={d_irms:.1f}, d_h1={d_h1:.1f}"
            )
            self._sync_baseline_to(win_feat)
            self._pending_off_drop = False  # v12: 상태 reset
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        # v34: delta_pf 도 drop dict 에 추가. baseline 의 PF 와 win 의 PF 차이.
        # 사용자가 PF 낮은 기기 (charger 0.17~0.34) 빼면 baseline PF 상승 → drop_pf 음수.
        # 사용자가 PF 높은 기기 (tv 0.42~0.50) 빼면 baseline PF 변화량 다름. sign 유지.
        baseline_pf = float(self.baseline_feat.get("PF_proxy_mean", 0.0)) if self.baseline_feat else 0.0
        win_pf = float(win_feat.get("PF_proxy_mean", 0.0))
        drop = {
            "delta_irms": max(0.0, self.baseline_irms - float(win_feat.get("Irms_adc_mean", 0.0))),
            "delta_h1": max(0.0, self.baseline_h1 - float(win_feat.get("H1_60_mag_mean", 0.0))),
            "delta_pabs": max(0.0, float(self.baseline_feat.get("Pabs_mean_proxy_mean", self.baseline_feat.get("Pabs_mean_proxy", 0.0))) - float(win_feat.get("Pabs_mean_proxy_mean", win_feat.get("Pabs_mean_proxy", 0.0)))),
            # v99: H5 drop. baseline H5 - win H5 (extensive 라 OFF 시 기기 H5 만큼 감소).
            "delta_h5": max(0.0, float(self.baseline_feat.get("H5_300_mag_mean", self.baseline_feat.get("H5_300_mag", 0.0))) - float(win_feat.get("H5_300_mag_mean", win_feat.get("H5_300_mag", 0.0)))),
            "delta_pf": baseline_pf - win_pf,  # 부호 유지 (sig 의 delta_pf 와 비교)
        }

        dev_name, score = self._select_off_device_by_signature(drop)

        # v53: OFF verify callback (orchestrator 토글 검증) 흐름.
        # 후보 결정 직후 토글로 부하 잔존 여부 검증 → false OFF 면 라벨 복원 + 재선출.
        # AIEngine 의 active_devices 는 *이 시점에는 아직 dev 가 들어 있다* (del 은 후술).
        # callback 안에서 SPI raw 측정 (engine.process_raw_mode) 로 Irms 비교.
        if dev_name is not None and self._off_verify_callback is not None:
            excluded = set()
            max_iter = len(self.active_devices) + 1
            iter_count = 0
            verify_cancelled = False
            while dev_name is not None and iter_count < max_iter:
                iter_count += 1
                try:
                    verdict = self._off_verify_callback(dev_name, drop, win_feat)
                except Exception as exc:  # noqa: BLE001
                    logging.warning(f"[OFF VERIFY] callback exception: {exc}; fallback confirm")
                    verdict = "confirm"

                if verdict == "confirm":
                    logging.info(
                        f"[OFF VERIFY CONFIRM] {dev_name} 토글 결과 부하 없음 → 진짜 OFF"
                    )
                    break
                elif verdict == "reject":
                    excluded.add(dev_name)
                    logging.info(
                        f"[OFF VERIFY REJECT] {dev_name} 토글 결과 부하 여전 → 재추론 "
                        f"(excluded={sorted(excluded)})"
                    )
                    dev_name, score = self._select_off_device_by_signature(drop, exclude=excluded)
                elif verdict == "cancel":
                    logging.warning(
                        f"[OFF VERIFY CANCEL] {dev_name} 매핑 lookup 실패 또는 검증 불가 → "
                        f"active 그대로 유지"
                    )
                    verify_cancelled = True
                    break
                else:
                    logging.warning(f"[OFF VERIFY] unknown verdict={verdict!r}; fallback confirm")
                    break

            if verify_cancelled or dev_name is None:
                # 모든 후보가 false OFF 거나 매핑 lookup 실패 → cascade 방어
                if not verify_cancelled:
                    logging.warning(
                        f"[OFF VERIFY EXHAUST] excluded={sorted(excluded)} 후 더 이상 후보 없음 → fallback 시도"
                    )

                # v54: cancel 직전 전수 토글 fallback.
                # cancel = 모든 sig 매칭 후보가 false 거나 후보가 비어 있음. 그러나 사용자가
                # 실제로 가전을 뽑은 경우 *어딘가 부재 socket* 이 있을 것 → 전수 토글로 찾기.
                fallback_dev = None
                if (not verify_cancelled) and self._off_verify_exhaust_fallback is not None:
                    try:
                        fallback_dev = self._off_verify_exhaust_fallback(
                            drop, win_feat, excluded
                        )
                    except Exception as exc:  # noqa: BLE001
                        logging.warning(f"[OFF VERIFY] exhaust fallback exception: {exc}")
                        fallback_dev = None

                if fallback_dev is not None and fallback_dev in self.active_devices:
                    logging.info(
                        f"[OFF VERIFY FALLBACK FORCE-OFF] dev={fallback_dev} 채택 → OFF 처리 진행"
                    )
                    dev_name = fallback_dev
                    score = 0.0
                    # fall through: 아래 정상 OFF 처리 흐름으로 진입
                else:
                    if fallback_dev is not None:
                        logging.warning(
                            f"[OFF VERIFY FALLBACK] dev={fallback_dev} 가 active_devices 에 없음 → cancel"
                        )
                    self._sync_baseline_to(win_feat)
                    self._pending_off_drop = False
                    self._consecutive_partial_rejects = 0
                    self._cascade_drop_history = []
                    self.event_cooldown = max(
                        EVENT_COOLDOWN_FRAMES, OFF_VERIFY_CANCEL_COOLDOWN_FRAMES
                    )
                    return

        if dev_name is None:
            logging.warning(f"[OFF REJECT] no matching active signature drop={drop}")
            # v15: REJECT 사유에 따라 baseline 처리 분기
            # - "partial": 실제 OFF 시작 중인 부분 drop → 동결하여 누적 대기 (v12 동작 유지)
            # - "oversized"/"guarded"/"low_score"/"too_small": high-power drain 잔향이거나 노이즈
            #   → baseline 을 win_feat 으로 동기화하여 drain 흡수, cascade 종료
            #   (이전 v12 만으로는 oversized REJECT 시에도 baseline 동결되어 drain 잔향이
            #    절대 흡수 안 되고 cascade 가 사용자 종료까지 무한 반복됨 - 실측 13회 24초간)
            if self._off_reject_reason == "partial":
                # v18: 연속 partial reject 가 3회 초과면 stable cascade (drop 안 자람) → 강제 sync
                self._consecutive_partial_rejects += 1
                # v30: 현재 cascade 의 drop_h1 추이 저장 (진짜 OFF vs noise 구별용)
                self._cascade_drop_history.append(float(drop.get("delta_h1", 0.0)))
                if self._consecutive_partial_rejects > 3:
                    # v30: drop 추이 검증. 진짜 OFF event 면 baseline frozen 상태에서 drop 점진적 증가
                    # → 마지막 drop ≈ max. cleaner duty cycle noise 면 drop 진동/감소.
                    # 실측 (2026-05-22 17:43:00-05): 사용자가 아무것도 안 건드림에도 cleaner duty cycle
                    # 변동의 drops=[355,322,263,267] cascade → v28 임계로 charger force OFF 가 잘못 발동.
                    # 마지막(267)이 max(355)의 90% 미만 → noise 로 판정해 baseline sync 만.
                    drops = self._cascade_drop_history
                    max_drop = max(drops) if drops else 0.0
                    # v31: 임계 0.9 → 0.7 완화. high-power 도미넌스로 last 가 max 보다 약간 작은
                    # 케이스도 진짜 OFF 일 수 있음 (예: tv 빼는 cascade last/max=0.79).
                    is_progressing = (
                        len(drops) >= 3 and drops[-1] >= max_drop * 0.7
                    )

                    if is_progressing:
                        # v27: cascade break 직전 누적 drop 을 active 기기 sig 와 매칭해서 force OFF 시도.
                        win_h1_now = float(win_feat.get("H1_60_mag_mean", 0.0))
                        accum_drop_h1 = self.baseline_h1 - win_h1_now  # baseline 은 frozen 상태
                        # v34: PF 도 함께 매칭. baseline PF - win PF 가 sig 의 delta_pf 와 매칭되는지 비교.
                        # charger PF=0.17~0.34 vs tv PF=0.42~0.50 의 명확한 차이를 활용해
                        # dH1 만으로 charger/tv 구별 못하는 ambiguous 케이스 해결 (실측 19:01:43, 19:02:01).
                        baseline_pf_now = float(self.baseline_feat.get("PF_proxy_mean", 0.0)) if self.baseline_feat else 0.0
                        win_pf_now = float(win_feat.get("PF_proxy_mean", 0.0))
                        accum_drop_pf = baseline_pf_now - win_pf_now

                        best_match_dev = None
                        best_match_ratio = float("inf")
                        best_match_detail = None
                        for dev in self.active_devices:
                            sig_dict = self.device_signatures.get(dev, {})
                            sig_h1 = abs(float(sig_dict.get("delta_h1", 0.0)))
                            sig_pf = float(sig_dict.get("delta_pf", 0.0))
                            if sig_h1 <= 0:
                                continue
                            # v28: 비대칭 임계. 작은 sig (< 3000) 30%, 큰 sig (≥ 3000) 50%.
                            lower_ratio = 0.30 if sig_h1 < 3000.0 else 0.50
                            if not (lower_ratio * sig_h1 <= accum_drop_h1 <= 1.5 * sig_h1):
                                continue
                            ratio_h1 = abs(accum_drop_h1 - sig_h1) / sig_h1
                            # v34: PF ratio 결합. sig_pf 가 충분히 크면 (|sig_pf|>=0.03) 가중치 적용.
                            # PF 부호 보존 — drop_pf 와 sig_pf 가 같은 부호이면서 크기 비슷할 때 매칭.
                            if abs(sig_pf) >= 0.03:
                                ratio_pf = abs(accum_drop_pf - sig_pf) / max(abs(sig_pf), 0.05)
                                combined_ratio = 0.6 * ratio_h1 + 0.4 * ratio_pf
                                detail = f"H1ratio={ratio_h1:.2f} PFratio={ratio_pf:.2f} drop_pf={accum_drop_pf:.3f} sig_pf={sig_pf:.3f}"
                            else:
                                combined_ratio = ratio_h1
                                detail = f"H1ratio={ratio_h1:.2f} (sig_pf negligible)"
                            if combined_ratio < best_match_ratio:
                                best_match_ratio = combined_ratio
                                best_match_dev = dev
                                best_match_detail = detail

                        # v38: high-power partial cascade 검증.
                        # 실측 (2026-05-23 00:15:24): microwave 의 부분 ramp-down drops=[2201,...,2187] 가
                        # microwave sig=17234 의 12.7% 영역 → 큰 sig 50% 임계 미달로 매칭 X.
                        # 그러나 tv sig=1500 의 146% 영역에 들어가 tv 가 잘못 force OFF.
                        # active high-power 가 있고 그 sig 의 10~50% 영역에 drop 이 누적 중이면
                        # high-power 의 partial cascade 진행 중으로 보고 force OFF 보류 → 다음 cycle 에
                        # 더 큰 drop 으로 정확히 매칭.
                        high_power_partial_dev = None
                        for dev_check, sig_dict_check in self.device_signatures.items():
                            if dev_check not in self.active_devices or dev_check == best_match_dev:
                                continue
                            # v42: LOW_POWER 기기는 잘못된 reclassify 로 sig 가 비정상 크게 잡힐 수
                            # 있어 HP PARTIAL HOLD 후보에서 제외 (HP 기기만 고려).
                            if dev_check in LOW_POWER_DEVICES:
                                continue
                            sig_h1_abs = abs(float(sig_dict_check.get("delta_h1", 0.0)))
                            if sig_h1_abs > 3000.0:
                                hp_ratio = accum_drop_h1 / sig_h1_abs if sig_h1_abs > 0 else 0
                                if 0.10 <= hp_ratio <= 0.50:
                                    high_power_partial_dev = (dev_check, sig_h1_abs, hp_ratio)
                                    break

                        if best_match_dev is not None and high_power_partial_dev is not None:
                            hp_dev, hp_sig, hp_r = high_power_partial_dev
                            logging.info(
                                f"[OFF CASCADE → HIGH-POWER PARTIAL HOLD] {hp_dev} sig_h1={hp_sig:.0f} 의 "
                                f"{hp_r*100:.1f}% drop 누적 중 → {best_match_dev} force OFF 보류 (다음 cycle 대기)"
                            )
                        elif best_match_dev is not None:
                            # v39/v96: dominant HP active 중 LP cascade force OFF 금지 (HP duty
                            # 노이즈 누적이 LP sig 와 우연 매치하는 것 방지). target sig 의 3배 이상
                            # (≥3000) HP 가 active 이면 금지. v96: 5→3배. 실측 (2026-05-31 04:30:23):
                            # cleaner(6130) duty drops=[250,289,383,588] 누적이 tv(1464) 매치 → tv
                            # 잘못 force OFF (cleaner 가 tv 의 4.2배라 5배 미달로 dominant 미인정,
                            # tv 켠 지 15초 만에 사라짐). 상세: nilm-fix-stack.
                            sig_h1_bm = abs(float(self.device_signatures.get(best_match_dev, {}).get("delta_h1", 0.0)))
                            has_dominant_hp = any(
                                abs(float(self.device_signatures.get(d, {}).get("delta_h1", 0.0))) > max(sig_h1_bm * 3, 3000.0)
                                for d in self.active_devices if d != best_match_dev
                            )
                            if has_dominant_hp and best_match_dev in LOW_POWER_DEVICES:
                                # v44: HP-dominant 시 force off 는 정말 정확할 때만 허용.
                                # 1) ratio 범위 0.95~1.05 (이전 0.85~1.15 는 너무 넓음 → 노이즈 force off 위험)
                                # 2) drops 마지막 성장률 < 5% (수렴 = 진짜 OFF, 계속 증가 = HP 노이즈)
                                # 실측 (2026-05-24 19:09:10): drops=[233,547,1332,1484] 의 tv ratio=0.96 이
                                # 0.85~1.15 통과해서 tv 잘못 force off (사용자는 charger 끄려 함, drops 는
                                # microwave 노이즈가 계속 증가 중인 패턴 — last_growth=11.4% 로 수렴 아님).
                                acc_ratio_strict = accum_drop_h1 / sig_h1_bm if sig_h1_bm > 0 else 0
                                last_growth = float("inf")
                                if len(drops) >= 2 and drops[-2] > 0:
                                    last_growth = abs(drops[-1] - drops[-2]) / drops[-2]
                                in_strict = (0.95 <= acc_ratio_strict <= 1.05)
                                stable = (last_growth < 0.05)
                                # v52j: stable + 누적이 sig 의 0.80~2.00 영역이면 force off 허용.
                                # 실측 (2026-05-27 17:36:48): dryer/cleaner 둘 다 active 중 사용자가 TV 끔.
                                # drops=[305, 674, 719, 736] 누적 2434 = tv sig=1499 의 162%. last_growth=
                                # (736-719)/719 = 2.4% < 5% → stable=True. v44 in_strict (0.95~1.05) 미달로
                                # HOLD → 이후 cond2 OFF 추가 안 발생 (TV ramp-down 점진적 → baseline EMA 따라감) →
                                # TV 영영 미인식.
                                # stable 이면 누적 drop 가 안정화된 상태 — 진짜 OFF 의 강한 단서. over-shoot
                                # (1.05~2.00) 도 사용자 OFF 의 cascade noise 합산일 뿐 진짜 OFF 사실 변함 없음.
                                in_overshoot = (0.80 <= acc_ratio_strict <= 2.00)
                                if in_strict and stable:
                                    logging.info(
                                        f"[OFF CASCADE → FORCE OFF MATCH (HP-DOMINANT precise)] {best_match_dev} "
                                        f"accum={accum_drop_h1:.1f} sig={sig_h1_bm:.1f} ratio={acc_ratio_strict:.2f} "
                                        f"last_growth={last_growth:.3f} → force off 허용; drops={drops}"
                                    )
                                    self._force_device_off(best_match_dev)
                                elif stable and in_overshoot:
                                    logging.info(
                                        f"[OFF CASCADE → FORCE OFF MATCH (HP-DOMINANT stable-overshoot)] "
                                        f"{best_match_dev} accum={accum_drop_h1:.1f} sig={sig_h1_bm:.1f} "
                                        f"ratio={acc_ratio_strict:.2f} last_growth={last_growth:.3f} "
                                        f"→ stable + 0.80~2.00 영역 force off; drops={drops}"
                                    )
                                    self._force_device_off(best_match_dev)
                                else:
                                    logging.info(
                                        f"[OFF CASCADE → HP-DOMINANT HOLD] dominant high-power active, "
                                        f"{best_match_dev} accum={accum_drop_h1:.1f} sig={sig_h1_bm:.1f} "
                                        f"ratio={acc_ratio_strict:.2f} in_strict={in_strict} "
                                        f"last_growth={last_growth:.3f} stable={stable} → HOLD"
                                    )
                            else:
                                logging.info(
                                    f"[OFF CASCADE → FORCE OFF MATCH] {best_match_dev} accum_drop_h1={accum_drop_h1:.1f}, "
                                    f"accum_drop_pf={accum_drop_pf:.3f} matches sig (ratio={best_match_ratio:.2f}, {best_match_detail}); drops={drops}"
                                )
                                self._force_device_off(best_match_dev)
                        else:
                            logging.info(
                                f"[OFF PARTIAL CASCADE BREAK] progressing but no sig match "
                                f"(accum_drop_h1={accum_drop_h1:.1f}, drops={drops}) → baseline 강제 sync"
                            )
                    else:
                        # v31: noise 패턴이지만 max drop 가 active low-power sig 와 매칭되면 force OFF.
                        # 실측 (2026-05-22 18:23:58~03): cleaner+dryer active 중 사용자 charger 빼는 cascade
                        # drops=[332,284,110,142] 가 high-power 도미넌스로 noise 처럼 보였으나 max=332 가
                        # charger sig=866 의 38% → 30% 영역 내. low-power 만 30% 임계 매칭 시도.
                        noise_match_dev = None
                        noise_match_ratio = float("inf")
                        for dev in self.active_devices:
                            if dev not in LOW_POWER_DEVICES:
                                continue
                            sig_h1 = abs(float(self.device_signatures.get(dev, {}).get("delta_h1", 0.0)))
                            if sig_h1 <= 0:
                                continue
                            if 0.30 * sig_h1 <= max_drop <= 1.50 * sig_h1:
                                ratio = abs(max_drop - sig_h1) / sig_h1
                                if ratio < noise_match_ratio:
                                    noise_match_ratio = ratio
                                    noise_match_dev = dev

                        if noise_match_dev is not None:
                            # v39: dominant high-power active → noise break low-power force OFF 비활성화
                            sig_h1_nm = abs(float(self.device_signatures.get(noise_match_dev, {}).get("delta_h1", 0.0)))
                            has_dominant_hp_nb = any(
                                abs(float(self.device_signatures.get(d, {}).get("delta_h1", 0.0))) > max(sig_h1_nm * 3, 3000.0)
                                for d in self.active_devices if d != noise_match_dev
                            )
                            if has_dominant_hp_nb and noise_match_dev in LOW_POWER_DEVICES:
                                logging.info(
                                    f"[OFF NOISE BREAK → HP-DOMINANT HOLD] dominant high-power active, "
                                    f"{noise_match_dev} noise break force OFF 비활성화"
                                )
                            else:
                                logging.info(
                                    f"[OFF NOISE BREAK → LOW-POWER FORCE OFF] {noise_match_dev} max_drop={max_drop:.1f} "
                                    f"matches sig (ratio={noise_match_ratio:.2f}); drops={drops} (high-power 도미넌스 noise)"
                                )
                                self._force_device_off(noise_match_dev)
                        else:
                            logging.info(
                                f"[OFF NOISE BREAK] drops={drops} (last={drops[-1]:.1f}, max={max_drop:.1f}); "
                                f"not progressing, no low-power match → baseline sync"
                            )

                    self._sync_baseline_to(win_feat)
                    self._pending_off_drop = False
                    self._consecutive_partial_rejects = 0
                    self._cascade_drop_history = []
                else:
                    self._pending_off_drop = True
                    # baseline 동결 (다음 frame d_h1 누적)
            else:
                # 잔향/노이즈 → baseline 동기화하여 cascade 종료
                self._sync_baseline_to(win_feat)
                self._pending_off_drop = False
                self._consecutive_partial_rejects = 0
                self._cascade_drop_history = []  # v30
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        sk_idx = self.active_devices.get(dev_name)
        target_sk = next((s for s in self.sockets if s.idx == sk_idx), None)
        if target_sk is None:
            logging.warning(f"[OFF FAIL] socket{sk_idx} not found")
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        target_sk.turn_off()
        del self.active_devices[dev_name]
        # v29: sig 를 history 에 백업 (재등록 시 dominance 로 작게 측정될 때 사용)
        sig_to_save = self.device_signatures.pop(dev_name, None)
        if sig_to_save is not None:
            self._backup_signature(dev_name, sig_to_save)
        self.device_on_frames.pop(dev_name, None)
        self.device_on_wallclock.pop(dev_name, None)
        if dev_name in HIGH_POWER_DEVICES:
            self.last_high_power_off_frame = self.frame_count
            # v46: HP OFF 후 30 frames 뒤 active LP 검증 (baseline 안정화 대기)
            if any(d in LOW_POWER_DEVICES for d in self.active_devices):
                self._hp_off_lp_cleanup_frame = self.frame_count + 30
        elif dev_name in LOW_POWER_DEVICES:
            self.last_lp_off_frame = self.frame_count  # v81: LP OFF 후 잔류 가드
        self.reclassify_countdown = 0
        self._pending_off_drop = False  # v12: 성공 OFF → 누적 대기 종료
        self._consecutive_partial_rejects = 0  # v18
        self._cascade_drop_history = []  # v30

        logging.info(
            f"[DEVICE OFF] Socket{target_sk.idx} ({dev_name}) by signature score={score:.2f}, "
            f"drop_I={drop['delta_irms']:.1f}, drop_H1={drop['delta_h1']:.1f}, drop_Pabs={drop['delta_pabs']:.1f}"
        )
        self.event_history.append((self.frame_count, "OFF", dev_name))
        self._sync_baseline_to(win_feat)
        self.event_cooldown = EVENT_COOLDOWN_FRAMES

        if not self.active_devices:
            self.idle_baseline_irms = self.baseline_irms
            self.idle_baseline_h1 = self.baseline_h1

    def _select_off_device_by_signature(self, drop, exclude=None):
        """
        OFF 이벤트에서 제거할 기기 선택.

        v7 핵심:
        - cleaner/dryer/microwave 같은 high-power 기기가 active일 때, 작은/중간 H1 감소를
          charger/tv OFF로 먼저 먹어버리면 데모 순서가 바로 꼬인다.
        - 따라서 high-power active가 있으면 low-power 후보는 일단 보호하고,
          high-power 쪽을 우선 제거한다.
        - 이번 로그에서 cleaner OFF 직후 drop_H1≈546, 619가 charger/tv OFF로 처리된 것이
          핵심 문제였으므로, 이 구간을 cleaner partial-off로 처리한다.

        v53: OFF verify callback 의 재선출용 exclude 인자.
        - 토글 검증으로 false OFF 판명된 라벨을 제외하고 다음 best 후보 반환.
        - exclude 된 라벨은 self.active_devices 에는 여전히 존재 (라벨 복원됨)
          → sanity 검증/dominance 검사 등에서는 *포함*되어야 함.
        - 후보 풀(active_names/high_active/low_active/candidates_scored) 에서만 제외.
        """
        # v15: reset reject reason at start of selection
        self._off_reject_reason = None

        if not self.active_devices:
            return None, float("inf")

        exclude = set(exclude) if exclude else set()
        active_names = [d for d in self.active_devices.keys() if d not in exclude]
        if not active_names:
            return None, float("inf")
        high_active = [d for d in active_names if d in HIGH_POWER_DEVICES]
        low_active = [d for d in active_names if d in LOW_POWER_DEVICES]

        drop_h1 = float(drop.get("delta_h1", 0.0))
        drop_i = float(drop.get("delta_irms", 0.0))
        drop_p = float(drop.get("delta_pabs", 0.0))
        drop_h5 = float(drop.get("delta_h5", 0.0))  # v100: charger/tv weak OFF 매치 구별용

        def low_power_off_guard_reason(dev):
            if dev not in LOW_POWER_DEVICES:
                return None
            age = self.frame_count - self.device_on_frames.get(dev, -10**9)
            if age < LOW_POWER_MIN_ACTIVE_FRAMES_BEFORE_OFF:
                # v52j: sig 매치가 매우 강하면 (h1_ratio AND i_ratio 둘 다 0.70~1.40) age guard 우회.
                # 실측 (2026-05-27 17:36:03): charger 등록 후 16초 (≈70f) 만에 사용자가 충전기 뽑음.
                # drop_H1=843, drop_I=19.3 vs sig=(872, 19.7) → h1_ratio=0.97, i_ratio=0.98 (거의 완벽 매치)
                # 그런데 age=70 < 85 임계로 reject → 충전기 OFF 영영 미인식 → 사용자가 다시 꽂았다 빼야 함.
                # 진짜 charger 의 자체 transient/ramp 는 sig 와 매치 안 됨 (sig 자체가 정상 등록 시 측정값).
                # sig 양쪽 (H1, I) 모두 강하게 매치되면 age 무관 진짜 OFF 로 인정 — false positive 위험 매우 낮음.
                dev_sig = self.device_signatures.get(dev, {})
                dev_sig_h1 = abs(float(dev_sig.get("delta_h1", 0.0)))
                dev_sig_i = abs(float(dev_sig.get("delta_irms", 0.0)))
                if dev_sig_h1 > 0:
                    h1_ratio = drop_h1 / dev_sig_h1
                    i_ratio = drop_i / dev_sig_i if dev_sig_i > 0 else 1.0
                    if (0.70 <= h1_ratio <= 1.40
                            and 0.70 <= i_ratio <= 1.40):
                        logging.info(
                            f"[LOW-POWER OFF GUARD BYPASS-AGE] {dev} age={age}f < "
                            f"{LOW_POWER_MIN_ACTIVE_FRAMES_BEFORE_OFF}f 이지만 sig 매치 강함 "
                            f"(h1_ratio={h1_ratio:.2f}, i_ratio={i_ratio:.2f}) → 실제 OFF 인정"
                        )
                        # age guard 우회 — since_hp_off / drop_too_small 검사로 계속
                    else:
                        return f"low-power active age too short ({age}f < {LOW_POWER_MIN_ACTIVE_FRAMES_BEFORE_OFF}f)"
                else:
                    return f"low-power active age too short ({age}f < {LOW_POWER_MIN_ACTIVE_FRAMES_BEFORE_OFF}f)"
            since_hp_off = self.frame_count - self.last_high_power_off_frame
            if since_hp_off < LOW_POWER_OFF_AFTER_HIGHPOWER_GUARD_FRAMES:
                # v19: drop 이 이 device sig 와 잘 매칭되면 (50-150%) 실제 low-power OFF 로 보고 guard 우회.
                # 실측: microwave OFF 27 frame 후 TV unplug 시 drop=1069 가 TV sig=1542 의 69% → guard 1f 차이로 누락됨.
                dev_sig = self.device_signatures.get(dev, {})
                dev_sig_h1 = abs(float(dev_sig.get("delta_h1", 0.0)))
                if dev_sig_h1 > 0 and 0.5 * dev_sig_h1 <= drop_h1 <= 1.5 * dev_sig_h1:
                    logging.info(
                        f"[LOW-POWER OFF GUARD BYPASS] {dev} drop_H1={drop_h1:.1f} ≈ sig_H1={dev_sig_h1:.1f}; "
                        f"실제 OFF 로 인정 (residue guard 우회)"
                    )
                else:
                    return f"recent high-power OFF residue ({since_hp_off}f < {LOW_POWER_OFF_AFTER_HIGHPOWER_GUARD_FRAMES}f)"
            # v81: LP relay OFF 후 잔류 신호(baseline 미정착)로 다른 LP 가 잘못 OFF 되는 케이스 방어.
            # 실측 (2026-05-30 18:49): TV OFF → relay OFF residue d_h1=-335.2 → charger OFF trigger
            # → exhaust fallback ΔI=+2.0(충전완료) → ratio=0.09 → "absent" 오판 → charger 강제 OFF.
            # drop 이 dev 의 sig 70% 미만인 작은 신호면 잔류로 간주하고 reject.
            since_lp_off = self.frame_count - self.last_lp_off_frame
            if since_lp_off < LP_OFF_AFTER_LOWPOWER_GUARD_FRAMES:
                dev_sig_lp = self.device_signatures.get(dev, {})
                dev_sig_h1_lp = abs(float(dev_sig_lp.get("delta_h1", 0.0)))
                if dev_sig_h1_lp > 0 and drop_h1 < 0.70 * dev_sig_h1_lp:
                    return f"recent low-power OFF residue ({since_lp_off}f < {LP_OFF_AFTER_LOWPOWER_GUARD_FRAMES}f, drop_H1={drop_h1:.1f} < 70% of sig={dev_sig_h1_lp:.1f})"
            if drop_h1 < LOW_POWER_OFF_MIN_DROP_H1 and drop_i < LOW_POWER_OFF_MIN_DROP_I:
                return f"low-power drop too small (drop_H1={drop_h1:.1f}, drop_I={drop_i:.1f})"
            return None

        # active가 1개뿐이면 방향성이 더 중요하다.
        if len(active_names) == 1:
            dev = active_names[0]
            reason = low_power_off_guard_reason(dev)
            if reason:
                logging.info(f"[LOW-POWER OFF GUARD] reject {dev} OFF | {reason}")
                # v40: drop 이 sig 의 30% 이상이면 partial 로 처리하여 cascade 누적 가능.
                # 실측 (2026-05-24 18:16:28): microwave OFF 21f 후 TV unplug 시 drop_h1=560.9
                # 가 sig=1572.4 의 35.7% → BYPASS(50% 임계) 미달이라 guarded 로 reject 됐고
                # baseline sync 로 cascade 도 못 쌓여 TV OFF 가 영영 못 감지됨.
                # partial 로 처리하면 baseline freeze + cascade 누적 → 4번째 cond2 OFF 에서
                # tv sig 매칭으로 force OFF 가능. (v39 의 HP-DOMINANT HOLD 는 microwave 가
                # 이미 OFF 됐으므로 발동 안 함 → 정상 force OFF.)
                dev_sig_h1_g = abs(float(self.device_signatures.get(dev, {}).get("delta_h1", 0.0)))
                if dev_sig_h1_g > 0 and drop_h1 >= dev_sig_h1_g * 0.30:
                    logging.info(
                        f"[LOW-POWER GUARD → CASCADE] {dev} drop_H1={drop_h1:.1f} >= 30% of sig={dev_sig_h1_g:.1f}; "
                        f"partial 누적 (실제 OFF 가능성)"
                    )
                    self._off_reject_reason = "partial"
                else:
                    self._off_reject_reason = "guarded"
                return None, float("inf")
            sig = self.device_signatures.get(dev, {})
            sig_h1 = abs(float(sig.get("delta_h1", 0.0)))
            sig_i = abs(float(sig.get("delta_irms", 0.0)))
            h1_min = max(120.0, sig_h1 * 0.08)
            i_min = max(5.0, sig_i * 0.06)
            if drop_h1 < h1_min and drop_i < i_min:
                self._off_reject_reason = "too_small"
                return None, float("inf")

            # v13/v61: LP single active 도 partial-drop(drop_H1 < sig 40%) reject → cascade
            # 누적. 통과분은 orchestrator OFF VERIFY 토글로 최종 검증. 상세: nilm-fix-stack.
            if dev in LOW_POWER_DEVICES and sig_h1 > 0 and drop_h1 < sig_h1 * 0.40:
                logging.info(
                    f"[OFF PARTIAL REJECT] {dev} single drop_H1={drop_h1:.1f} < 40% of sig_H1={sig_h1:.1f}; "
                    f"high-power 잔향 가능성, 누적 대기"
                )
                self._off_reject_reason = "partial"
                return None, float("inf")

            # v13: low-power single active 에서의 over-sized drop reject.
            # 예: microwave OFF 후 charger single active, drop_h1=10723 인데 charger sig_h1=62.
            # low-power 가전의 실제 OFF drop 은 sig 근처(±50%)여야 함. sig 의 2배 이상은 high-power 잔향.
            # 절대 임계 1500 도 같이 둠 - sig 가 ramp 도중 작게 잡힌 경우(예: charger sig=62) 보호.
            if dev in LOW_POWER_DEVICES and drop_h1 > max(sig_h1 * 2.0, 1500.0):
                logging.info(
                    f"[OFF OVERSIZED REJECT] {dev} single drop_H1={drop_h1:.1f} > "
                    f"max(2*sig_H1={sig_h1*2:.1f}, 1500); high-power drain 잔향"
                )
                self._off_reject_reason = "oversized"
                return None, float("inf")

            return dev, 0.0

        def score_for(dev):
            sig = self.device_signatures.get(dev, {})
            score = 0.0
            # v34: PF 항 추가. charger PF=0.17~0.34 vs tv PF=0.42~0.50 의 명확한 차이를
            # multi-active general path 에도 활용 (cascade reject 후 후속 cond2 OFF 매칭).
            # v34: PF 항. (v98 에서 PF 가중 0.35 로 올렸다 롤백: OFF 의 *변화량* delta_pf 는
            # 실측 ~0.01 로 너무 작아—baseline PF 가 지배—가중 ↑ 시 0.03 임계에 막힘. charger/tv 의
            # *절대* PF 단서는 RF 분류가 이미 활용. → PF 변화량은 OFF 매칭에 약함.)
            # v99: delta_h5 항 추가(가중 0.25). H5 는 extensive 라 OFF drop 이 큼(charger 597 vs
            # tv 117) → PF(변화량 ~0.01)와 달리 매칭에 유효. 복제검증: charger/tv OFF 정확도
            # 95.1→97.1%, 분리도 0.177→0.247. 기존 4항 가중을 0.45/0.20/0.15/0.20 에서 낮춰 합 1.0.
            for key, weight in [("delta_h1", 0.35), ("delta_irms", 0.15), ("delta_pabs", 0.10), ("delta_pf", 0.15), ("delta_h5", 0.25)]:
                a_raw = float(sig.get(key, 0.0))
                b_raw = float(drop.get(key, 0.0))
                if key == "delta_pf":
                    # PF 는 부호 보존. sig 와 drop 둘 다 baseline-win 형식이라 부호 일치 기대.
                    if abs(a_raw) < 0.03:
                        # sig 의 PF 변화가 의미 없음 → 가중치 0
                        continue
                    denom = max(abs(a_raw), 0.05)
                    score += weight * abs(a_raw - b_raw) / denom
                else:
                    a = abs(a_raw)
                    b = abs(b_raw)
                    denom = max(a, b, 1.0)
                    score += weight * abs(a - b) / denom
            return score

        # high-power 기기가 켜져 있는 동안의 작은 OFF 이벤트는 low-power OFF로 보내지 않는다.
        # 특히 cleaner OFF 직후의 부분 감소가 charger/tv signature와 더 가까워 보이는 문제가 있었다.
        if high_active:
            # 드라이기/청소기/전자레인지 중 가장 최근에 켜진 high-power를 우선 후보로 둔다.
            # dict는 삽입 순서를 유지하므로 뒤쪽일수록 최근에 ON된 기기다.
            recent_high = None
            for d in reversed(active_names):
                if d in HIGH_POWER_DEVICES:
                    recent_high = d
                    break

            best_high = min(high_active, key=score_for)
            # 최근 high-power와 score상 best가 다르면, 작은 partial drop에서는 최근 high를 더 믿는다.
            chosen_high = recent_high or best_high
            high_score = score_for(chosen_high)

            low_guard_region = (
                (drop_h1 >= HIGHPOWER_PARTIAL_OFF_MIN_H1 or drop_i >= HIGHPOWER_PARTIAL_OFF_MIN_I)
                and (drop_h1 < LOW_POWER_OFF_WHILE_HIGHPOWER_GUARD_H1
                     and drop_i < LOW_POWER_OFF_WHILE_HIGHPOWER_GUARD_I)
            )

            if low_guard_region:
                # v48~v50: HP active 중 LP sig 강매치 후보를 HIGH-POWER PARTIAL 보다 우선
                # 채택. HP sig 25% 미만 drop 영역이 LP sig 와 겹쳐 LP OFF 가 영영 묻히는 것
                # 방지. H1 단독 매치는 false positive 많아 drop_i 매치도 요구(v49). sig 절대값에
                # 따라 매치범위 동적 확장(작은 sig 는 HP 노이즈로 출렁, v50). 상세: nilm-fix-stack.
                lp_match = None
                lp_match_score = float("inf")
                lp_match_i_ratio = None
                lp_match_h1_ratio = None
                # v52: match_score 에 i_ratio 도 반영(max distance) + i_ratio 하한으로
                # "작은 LP drop + HP 노이즈가 큰 LP 흉내" false positive 거절. 상세: nilm-fix-stack.
                for d in low_active:
                    sig_d_h1 = abs(float(self.device_signatures.get(d, {}).get("delta_h1", 0.0)))
                    sig_d_i = abs(float(self.device_signatures.get(d, {}).get("delta_irms", 0.0)))
                    if sig_d_h1 <= 0:
                        continue
                    # v50: sig 절대값에 따라 매치 범위 동적 확장
                    if sig_d_h1 < 500.0:
                        # v83: h1_lower 0.3 → 0.55. HP active 상태에서 dryer 소듀티 노이즈
                        # (예: d_h1=240 = sig 의 50%) 가 small-sig charger 와 우연히 매치해
                        # 잘못된 LP OFF 시도 + standby guard contamination 을 유발.
                        # 실제 charger OFF 는 h1_ratio ≥ 0.85 이상이므로 0.55 는 안전.
                        h1_lower, h1_upper = 0.55, 3.5
                        i_lower, i_upper = 0.4, 4.0
                    else:
                        # v52: i_ratio 하한 0.5 → 0.80 강화 (large-sig branch only).
                        # 작은 LP 가 빠진 drop 이 큰 LP 의 sig 와 H1 매치 + drop_i 가 작아
                        # 보이는 false positive 거절.
                        #
                        # v52b: h1_lower 0.55 → 0.80 추가 강화.
                        # 실측 (2026-05-27 02:10:31): charger 미등록 (ON SKIP) 상태에서
                        # 약 20 초 뒤 cleaner duty-cycle / charger 자연 변동으로 drop=
                        # (11.6, 453.9) 발생. tv sig=(14.0, 595.5) 와 h1_ratio=0.76,
                        # i_ratio=0.83 양쪽 통과 → tv 잘못 OFF.
                        # 진짜 LP OFF 면 drop_h1 ≈ sig_h1; h1_ratio 0.55~0.80 영역은
                        # "partial drop" — HP duty-cycle 노이즈가 LP sig 의 부분을
                        # 흉내냄. cascade 누적으로 위임해 더 큰 drop 등장 시 매칭.
                        # 진짜 LP OFF + cleaner UP-beat 노이즈 합쳐진 케이스 (drop 축소)
                        # 는 일시적, 다음 frame 에서 cleaner cycling 시 drop 회복 →
                        # cascade 가 catch.
                        h1_lower, h1_upper = 0.80, 1.7
                        i_lower, i_upper = 0.80, 1.8
                    h1_ratio = drop_h1 / sig_d_h1
                    # v100 (사용자 제안: "빠지면 토글로 확인"): H5 강매치면 weak h1(0.45+) 허용.
                    # charger H5≈597 vs tv H5≈117 → H5 가 charger/tv 를 구별하므로 둘 다 active
                    # 여도 올바른 LP 선택. HP(cleaner/dryer) active 중 LP 를 천천히 빼 H1 이 HP duty
                    # 노이즈에 묻혀 작게(0.45~0.80 partial) 측정돼도, H5 가 그 LP sig 와 매치하면
                    # OFF 후보로 채택 → 최종 OFF VERIFY 토글이 확인(false positive 안전). cleaner/
                    # dryer 는 low_active 가 아니라 이 루프(low_active) 밖이라 LP 로 오인 안 됨.
                    # 실측 (2026-05-31 16:17:36~18:02): cleaner active 중 charger 뺌 drop H1 이
                    # cleaner sig 5%·charger sig 33% 로 H1 게이트 0.80 미달 → HIGH-POWER PARTIAL
                    # reject 26 초 지연. 헐거운 접촉(첫 drop 33%)은 0.45 도 미달이라 한계지만,
                    # 정상 빼기(50%+)는 H5 매치로 즉시 OFF VERIFY 위임.
                    sig_d_h5 = abs(float(self.device_signatures.get(d, {}).get("delta_h5", 0.0)))
                    h5_ratio = (drop_h5 / sig_d_h5) if sig_d_h5 > 30.0 else None
                    h5_strong = (h5_ratio is not None and 0.50 <= h5_ratio <= 1.6)
                    h1_weak_ok = h5_strong and (0.45 <= h1_ratio <= h1_upper)
                    if not ((h1_lower <= h1_ratio <= h1_upper) or h1_weak_ok):
                        continue
                    if h1_weak_ok:
                        i_lower = 0.40  # weak(H5 로 확인된) 매치는 i_ratio 하한 완화
                    # v49: drop_i 매치 검사
                    i_ratio = 1.0
                    i_exempt = False
                    if sig_d_i > 0:
                        i_ratio = drop_i / sig_d_i
                        # v92: HP active 중 LP unplug 시 drop_i 가 HP 대전류 노이즈에 묻혀
                        # 작게 측정되면(LP unplug 전형) i_ratio 하한 면제. H1 이 LP 의 신뢰 식별자.
                        # v95: 상한 1.30→1.55. HP 노이즈로 drop_h1 도 부풀어 h1_ratio 가 1.47 까지
                        # 튀어 charger 누락(2026-05-31 03:39:58: 충전기 뺌 drop=(6.2,1383) vs
                        # charger sig=(15.3,943) → h1_ratio=1.47, tv 는 age guard 로 빠져 lp_match
                        # 없음 → HP-PARTIAL reject). drop_i<12 게이트로 false positive 억제, 최종
                        # 검증은 OFF VERIFY 토글. 상세: nilm-fix-stack.
                        i_exempt = (0.80 <= h1_ratio <= 1.55 and drop_i < 12.0)
                        if i_ratio > i_upper:
                            continue
                        if i_ratio < i_lower and not i_exempt:
                            continue
                    guard_reason = low_power_off_guard_reason(d)
                    if guard_reason is not None:
                        continue
                    # v52: match_score 에 i_ratio 도 반영. h1_ratio 만 보면 비슷한 sig_h1 을
                    # 가진 다른 LP 와 우연히 더 잘 맞는 후보가 선택돼 오인식 발생.
                    # v92: i_ratio 면제된 (HP 노이즈로 drop_i 신뢰 불가) 후보는 h1_dist 만으로
                    # 점수. (어느 LP 를 먼저 고르든 OFF VERIFY 토글이 정확한 socket 을 확정.)
                    h1_dist = abs(1.0 - h1_ratio)
                    if i_exempt:
                        match_score = h1_dist
                    else:
                        i_dist = abs(1.0 - i_ratio) if sig_d_i > 0 else 0.0
                        match_score = max(h1_dist, i_dist)
                    if match_score < lp_match_score:
                        lp_match = d
                        lp_match_score = match_score
                        lp_match_i_ratio = i_ratio
                        lp_match_h1_ratio = h1_ratio

                if lp_match is not None:
                    lp_match_sig_h1 = abs(float(self.device_signatures.get(lp_match, {}).get("delta_h1", 0.0)))
                    lp_match_sig_i = abs(float(self.device_signatures.get(lp_match, {}).get("delta_irms", 0.0)))

                    # v93: lp_match 가 sig 와 정밀 일치 (i_ratio, h1_ratio 둘 다 ~1.0) 면
                    # 진짜 LP OFF. OFF VERIFY 릴레이 토글이 최종 검증하므로 v78 의 HP-partial
                    # suspect 보류를 적용하지 않고 채택한다. 실측 (2026-05-31 01:37:13~15):
                    # tv 뽑음 drop=(28.3,1507.9) vs tv sig=(28,1397) → h1_ratio=1.08,
                    # i_ratio=1.01 강매치인데, drop_h1 이 cleaner sig(6267) 의 24% 라 v78 이
                    # 보류 → tv 영구 미인식 (그 사이 baseline 이 drop 흡수). v78 이 막으려던
                    # cleaner-partial→tv 오매칭은 OFF VERIFY 가 tv 소켓 토글 시 살아있는 tv 의
                    # residual band ratio 로 reject → cascade 가 cleaner 잡음 (검증 위임).
                    strong_lp_match = (
                        lp_match_h1_ratio is not None and lp_match_i_ratio is not None
                        and 0.80 <= lp_match_h1_ratio <= 1.30
                        and 0.80 <= lp_match_i_ratio <= 1.30
                    )

                    # v78: HP active 의 partial drop 검증. drop 이 HP sig 의 partial 영역
                    # (15~35%) 이면 HP ramp-down 의 일부일 가능성. LP MATCH 보류, cascade 위임.
                    # 실측 (2026-05-30 00:33:23): 사용자 cleaner unplug → drop=(31.3, 1472.7).
                    # tv sig=(32, 1758) 와 i_ratio=0.98, h1_ratio=0.84 매치. 그러나 cleaner sig
                    # =(117, 6732) 의 22% partial drop 도 가능 (cleaner 의 자연스러운 ramp-down
                    # 초기). LP-우선 정책으로 tv 잘못 선택 → tv force OFF + 청소기 늦게 잡힘.
                    # v93: strong_lp_match 면 이 검사를 건너뛴다 (OFF VERIFY 위임).
                    hp_partial_suspect = None
                    hp_partial_ratio = 0.0
                    if not strong_lp_match:
                        for hp_d in self.active_devices:
                            if hp_d not in HIGH_POWER_DEVICES:
                                continue
                            hp_sig_h1 = abs(float(
                                self.device_signatures.get(hp_d, {}).get("delta_h1", 0.0)
                            ))
                            if hp_sig_h1 <= 0:
                                continue
                            r = drop_h1 / hp_sig_h1
                            if 0.15 <= r <= 0.35:
                                hp_partial_suspect = hp_d
                                hp_partial_ratio = r
                                break

                    if hp_partial_suspect is not None:
                        logging.info(
                            f"[OFF LP-MATCH HP-PARTIAL SUSPECT] drop_h1={drop_h1:.1f} 가 HP "
                            f"{hp_partial_suspect} sig 의 {hp_partial_ratio*100:.0f}% "
                            f"(15~35% partial 영역) → LP MATCH ({lp_match}) 보류, cascade 위임"
                        )
                        # LP MATCH skip. 일반 cascade 가 누적 drop 으로 정확한 dev 판단.
                    else:
                        logging.info(
                            f"[OFF LP MATCH AMID HP] {lp_match} sig=(dI={lp_match_sig_i:.1f},dH1={lp_match_sig_h1:.1f}) "
                            f"matches drop=(dI={drop_i:.1f},dH1={drop_h1:.1f}) "
                            f"h1_ratio={lp_match_h1_ratio:.2f} i_ratio={lp_match_i_ratio:.2f}; "
                            f"high-power active 이지만 low-power OFF 우선"
                        )
                        return lp_match, min(score_for(lp_match), 0.95)

                # v17: PRIORITY 경로에서도 partial check.
                # 실측: dryer ON 도중 heating element duty cycle 변동으로 drop_h1=1472 (sig 37497 의 3.9%)
                # 가 발생했는데 PRIORITY 가 즉시 dryer OFF 확정해버려 사용자가 안 껐는데도 OFF 표시됨.
                # PRIORITY 경로는 본래 "small drop while high-power active = high-power 의 일부 변동"
                # 가정인데, 변동만으로 즉시 OFF 확정하면 안 됨. 25% 미만이면 누적 대기.
                chosen_sig = self.device_signatures.get(chosen_high, {})
                chosen_sig_h1 = abs(float(chosen_sig.get("delta_h1", 0.0)))
                if chosen_sig_h1 > 0 and drop_h1 < chosen_sig_h1 * 0.25:
                    logging.info(
                        f"[OFF HIGH-POWER PARTIAL (priority)] {chosen_high} drop_H1={drop_h1:.1f} < "
                        f"25% of sig_H1={chosen_sig_h1:.1f}; duty cycle 변동 가능성, 누적 대기"
                    )
                    self._off_reject_reason = "partial"
                    return None, float("inf")

                logging.info(
                    f"[OFF HIGH-POWER PRIORITY] {chosen_high} selected over low-power candidates | "
                    f"drop_I={drop_i:.1f}, drop_H1={drop_h1:.1f}, score={high_score:.2f}"
                )
                return chosen_high, min(high_score, 0.95)

            # 큰 감소라면 high-power signature와 가장 가까운 쪽을 선택.
            if drop_h1 >= LOW_POWER_OFF_WHILE_HIGHPOWER_GUARD_H1 or drop_i >= LOW_POWER_OFF_WHILE_HIGHPOWER_GUARD_I:
                # v16: drop 이 best_high sig 의 25% 미만이면 ramp-down 초기로 보고 누적 대기.
                # 실측: dryer ON 후 5초만에 cond2 OFF d_h1=-3333 으로 즉시 OFF 확정됨.
                # 그러나 dryer sig=37325 의 8.9% 만 drop 한 시점이라 UI 가 너무 빨리 OFF 됨.
                # baseline frozen 으로 누적 대기 → drop 이 sig 의 25% 도달 후 확정.
                #
                # v33: best_high (sig 거리 가장 가까움) 와 recent_high (가장 최근 ON 된 high-power)
                # 가 다를 때, ramp-down 초기 drop 은 sig 의 일부라 *다른* high-power 의 partial 영역과
                # 우연히 더 가까워 보일 수 있음. score 차이가 2배 미만이면 recent_high 우선.
                # 실측 (2026-05-22 18:53:14): cleaner+microwave active 중 사용자 microwave 끄는데
                # microwave ramp-down drop=2250 이 cleaner sig 의 partial 영역과 우연히 더 가까워
                # cleaner 가 잘못 OFF 됨. recent_high=microwave 우선 선택하면 PARTIAL reject → 다음
                # cycle 에 큰 drop 으로 microwave OFF 정확히 매칭.
                chosen_target = best_high
                if recent_high is not None and recent_high != best_high:
                    recent_score = score_for(recent_high)
                    best_high_score = score_for(best_high)
                    if best_high_score > 0 and recent_score / best_high_score < 2.0:
                        logging.info(
                            f"[OFF HIGH-POWER RECENT-PRIORITY] {recent_high} chosen over {best_high} "
                            f"(score ratio={recent_score / best_high_score:.2f} < 2.0); "
                            f"ramp-down 초기 가능성"
                        )
                        chosen_target = recent_high

                best_high_sig = self.device_signatures.get(chosen_target, {})
                best_high_sig_h1 = abs(float(best_high_sig.get("delta_h1", 0.0)))
                if best_high_sig_h1 > 0 and drop_h1 < best_high_sig_h1 * 0.25:
                    logging.info(
                        f"[OFF HIGH-POWER PARTIAL] {chosen_target} drop_H1={drop_h1:.1f} < 25% of sig_H1={best_high_sig_h1:.1f}; "
                        f"ramp-down 초기, baseline 동결 후 누적 대기"
                    )
                    self._off_reject_reason = "partial"
                    return None, float("inf")

                # v52d: HP-CASCADE GUARD
                # 여러 HP 동시 active 인 상태에서 chosen_target 이 SMALLER sig HP 일 때
                # (즉 더 큰 HP 가 같이 active), drop 이 작은 HP 의 full OFF 모양으로 보이면서
                # 동시에 큰 HP 의 partial ramp-down 영역과 겹치는 ambiguity 발생.
                # 실측 (2026-05-27 15:02:12): dryer (sig_H1=35524) + cleaner (sig_H1=5735) active
                # 중 사용자가 dryer 끔. 1단계 drop_H1=4087 = cleaner sig 의 71% (full OFF 처럼 보임)
                # = dryer sig 의 11.5% (partial). 25% 임계 통과 → cleaner 잘못 OFF.
                # 그 다음 단계 drop_H1=4485 가 partial reject 됐고 결국 drop=18573 으로 dryer OFF
                # 됐으나 cleaner 는 영영 cascade.
                # 안전 가드: chosen_target 이 작은 sig + 더 큰 HP 동시 active 면 drop 가 sig 의 80%
                # 이상 되어야 채택. 그 미만은 큰 HP partial 의 우연 매치 가능성이 높음.
                if len(high_active) >= 2 and best_high_sig_h1 > 0:
                    other_hp_sigs_h1 = [
                        abs(float(self.device_signatures.get(d, {}).get("delta_h1", 0.0)))
                        for d in high_active if d != chosen_target
                    ]
                    if other_hp_sigs_h1 and max(other_hp_sigs_h1) > best_high_sig_h1:
                        if drop_h1 < best_high_sig_h1 * 0.80:
                            logging.info(
                                f"[OFF HP-CASCADE GUARD] {chosen_target} drop_H1={drop_h1:.1f} < 80% of "
                                f"sig_H1={best_high_sig_h1:.1f} AND larger HP sig({max(other_hp_sigs_h1):.0f}) "
                                f"동시 active; 큰 HP ramp-down partial 우연 매치 가능성, 누적 대기"
                            )
                            self._off_reject_reason = "partial"
                            return None, float("inf")

                # v52h: HP-CASCADE OVER-MATCH SWAP
                # chosen_target 이 작은 sig HP 인데 drop 이 그 sig 의 150% 초과 (over-shoot) 면
                # 작은 HP 단독 OFF 로 설명 불가능. 다른 active HP 중 drop 을 더 잘 설명하는 후보로 swap.
                # 실측 (2026-05-27 16:59:13): dryer (sig=18018) + cleaner (sig=5902) active 중 사용자가
                # dryer 끔. drop_H1=13901 = cleaner sig 의 235% (over-shoot) = dryer sig 의 77% (거의 full).
                # RECENT-PRIORITY 가 cleaner 채택 → 기존 HP-CASCADE GUARD 는 drop > sig*0.80 영역이라
                # 통과 → cleaner 잘못 OFF cascade.
                # OVER-SHOOT 검증: chosen sig 의 1.5배 초과면 다른 HP 중 ratio 0.70~1.20 안에 잘 맞는
                # 후보를 찾아 swap. ratio 가 그 안에 없으면 누적 대기.
                if len(high_active) >= 2 and best_high_sig_h1 > 0 and drop_h1 > best_high_sig_h1 * 1.5:
                    swap_hp = None
                    swap_ratio = None
                    swap_diff = float("inf")
                    for d in high_active:
                        if d == chosen_target:
                            continue
                        d_sig = abs(float(self.device_signatures.get(d, {}).get("delta_h1", 0.0)))
                        if d_sig <= 0:
                            continue
                        r = drop_h1 / d_sig
                        if 0.40 <= r <= 1.20:
                            diff = abs(r - 1.0)
                            if diff < swap_diff:
                                swap_diff = diff
                                swap_hp = d
                                swap_ratio = r
                    if swap_hp is not None and swap_ratio >= 0.70:
                        logging.info(
                            f"[OFF HP-CASCADE OVER-SWAP] {chosen_target} (sig={best_high_sig_h1:.0f}) "
                            f"drop_H1={drop_h1:.1f} over-shoot (ratio={drop_h1/best_high_sig_h1:.2f} > 1.5) → "
                            f"swap to {swap_hp} (sig={abs(float(self.device_signatures.get(swap_hp, {}).get('delta_h1', 0.0))):.0f}, "
                            f"ratio={swap_ratio:.2f} near-full OFF)"
                        )
                        chosen_target = swap_hp
                    elif swap_hp is not None:
                        # swap_ratio < 0.70: partial of larger HP — 누적 대기
                        logging.info(
                            f"[OFF HP-CASCADE OVER GUARD] {chosen_target} drop_H1={drop_h1:.1f} over-shoot AND "
                            f"larger HP {swap_hp} 의 partial (ratio={swap_ratio:.2f} < 0.70) → 누적 대기"
                        )
                        self._off_reject_reason = "partial"
                        return None, float("inf")
                    else:
                        # 어떤 다른 HP 도 잘 설명 못함 — over-shoot 인데 단서 부족, 누적 대기
                        logging.info(
                            f"[OFF HP-CASCADE OVER REJECT] {chosen_target} drop_H1={drop_h1:.1f} > "
                            f"sig*1.5={best_high_sig_h1*1.5:.0f} 이지만 다른 HP 와도 매치 안 됨, 누적 대기"
                        )
                        self._off_reject_reason = "partial"
                        return None, float("inf")

                logging.info(
                    f"[OFF HIGH-POWER MATCH] {chosen_target} selected | "
                    f"drop_I={drop_i:.1f}, drop_H1={drop_h1:.1f}, score={score_for(chosen_target):.2f}"
                )
                return chosen_target, min(score_for(chosen_target), 0.95)

        # v11 수정: 마지막 TV OFF만 별도 보정.
        # 이전 v10 로그에서 TV OFF 시 drop_H1≈899, drop_I≈6.9였는데,
        # signature 거리상 charger가 더 가까워 보여 TV OFF가 누락됐다.
        # charger ON/OFF는 건드리지 않고, tv가 active인 경우에만 좁게 적용한다.
        # v11 수정: 마지막 TV OFF만 별도 보정하되, Charger 서명이 완벽히 일치하면 뺏지 않음.
        if "tv" in active_names and not high_active:
            tv_age = self.frame_count - self.device_on_frames.get("tv", -10**9)
            since_hp_off = self.frame_count - self.last_high_power_off_frame
            tv_off_like = (
                tv_age >= TV_OFF_ONLY_MIN_TV_AGE_FRAMES
                and since_hp_off >= TV_OFF_ONLY_AFTER_HIGHPOWER_FRAMES
                and TV_OFF_ONLY_MIN_DROP_H1 <= drop_h1 <= TV_OFF_ONLY_MAX_DROP_H1
                and drop_i >= TV_OFF_ONLY_MIN_DROP_I
            )
            if tv_off_like:
                tv_score = score_for("tv")
                charger_score = score_for("charger") if "charger" in active_names else float("inf")

                # v47: drop_h1 이 tv_sig_h1 의 55% 미만이면 TV OFF 채택 금지 → 일반 경로 위임.
                # 일반 경로의 [OFF PARTIAL REJECT] 와 동일 임계지만 TV GUARD 가 그 전에 return 해
                # 우회되어 buried 되는 케이스 보완. score_for 는 PF 항(0.20 weight) 때문에
                # charger_score 가 부풀려져 SKIP 조건(charger_score<0.6 AND <tv_score) 이
                # 못 잡는 경우가 있음 (charger ON 시점 baseline PF 와 OFF 시점 baseline PF 가
                # 달라서 sig_pf vs drop_pf 부호/크기 어긋남).
                # 실측 (2026-05-24 20:00:42): drop_h1=716.5, tv_sig=1482.4 (48%),
                # charger_sig=671.1 (107% perfect match) → 그런데 TV 가 선택되어 charger OFF
                # 가 묻힘. 이 신규 SKIP 으로 일반 경로 → score_for 비교 → charger 정상 detect.
                tv_sig_h1_guard = abs(float(self.device_signatures.get("tv", {}).get("delta_h1", 0.0)))
                drop_too_small_for_tv = (
                    tv_sig_h1_guard > 0 and drop_h1 < tv_sig_h1_guard * 0.55
                )

                if drop_too_small_for_tv:
                    logging.info(
                        f"[TV OFF ONLY GUARD SKIP] drop_H1={drop_h1:.1f} < 55% of "
                        f"tv_sig_H1={tv_sig_h1_guard:.1f} (partial drop); 일반 경로로 위임"
                    )
                # 💡 핵심 방어막: 충전기 서명이 훨씬 완벽하게 일치하면 TV 가드를 강제 패스함
                elif charger_score < 0.6 and charger_score < tv_score:
                    logging.info(
                        f"[TV OFF ONLY GUARD SKIP] charger score({charger_score:.2f}) is much better "
                        f"than tv score({tv_score:.2f}). Real charger OFF detected."
                    )
                else:
                    logging.info(
                        f"[TV OFF ONLY GUARD] tv selected | "
                        f"drop_I={drop_i:.1f}, drop_H1={drop_h1:.1f}, "
                        f"tv_age={tv_age}f, since_hp_off={since_hp_off}f, tv_score={tv_score:.2f}"
                    )
                    return "tv", min(tv_score, 0.95)

        # high-power가 없거나 보호 조건이 아니면 기존 signature matching 수행.
        # v10: 저전력 기기는 age/high-power-residue guard를 통과한 경우에만 OFF 후보로 둔다.
        guarded = []
        candidates_scored = []
        for dev in active_names:
            reason = low_power_off_guard_reason(dev)
            if reason:
                guarded.append((dev, reason))
                continue
            candidates_scored.append((dev, score_for(dev)))

        if not candidates_scored:
            for dev, reason in guarded:
                logging.info(f"[LOW-POWER OFF GUARD] reject {dev} OFF | {reason}")
            # v40: 모든 후보가 guarded 라도 가장 큰 sig 의 기기에 대해 drop 이 30% 이상이면 partial
            largest_sig = 0.0
            largest_dev = None
            for d, _ in guarded:
                s = abs(float(self.device_signatures.get(d, {}).get("delta_h1", 0.0)))
                if s > largest_sig:
                    largest_sig = s
                    largest_dev = d
            if largest_dev and largest_sig > 0 and drop_h1 >= largest_sig * 0.30:
                logging.info(
                    f"[LOW-POWER GUARD → CASCADE] all guarded, but drop_H1={drop_h1:.1f} "
                    f">= 30% of largest sig {largest_dev}={largest_sig:.1f}; partial 누적"
                )
                self._off_reject_reason = "partial"
            else:
                self._off_reject_reason = "guarded"
            return None, float("inf")

        candidates_scored.sort(key=lambda x: x[1])
        best_dev, best_score = candidates_scored[0]

        # v23: low-power ambiguous tie-breaker (LIFO).
        # 실측 (2026-05-22 13:16:15): TV/charger 의 sig 가 거의 동일 (charger sig_h1=955,
        # tv sig_h1=1442) 한데 drop_h1=640 은 charger 의 67% / TV 의 44% 양쪽 모두 그럴듯.
        # signature score 만 보면 charger(0.44) < tv(0.49) 로 charger 가 선택되어 실제 TV 의
        # partial ramp-down 이 charger OFF 로 잘못 처리됨. 데이터로 ambiguous 한 경우, 사용자
        # 습관상 마지막에 꽂은 기기를 먼저 빼는 경향이 강하므로 LIFO (가장 최근 ON) 우선.
        # v75: LIFO TIE-BREAK gap 임계 0.15 → 0.05 강화.
        # 실측 (2026-05-29 20:52:49): charger pull → drop=(dI=18.3, dH1=773.6) → 매치
        # score: charger=0.24 (강함), tv=0.34 (약함). score 차이 0.10 명시적이지만 v74 임계
        # 0.15 미달이라 LIFO 가 tv (more recent ON) 선택 → 사용자가 charger 뽑았는데
        # tv_off 표시 ❌. score 0.10 차이는 매치 우열 명확 (charger 가 진짜 OFF). LIFO 는
        # 진짜 동률 (gap < 0.05) 일 때만 적용해야.
        if len(candidates_scored) >= 2:
            second_dev, second_score = candidates_scored[1]
            score_gap = second_score - best_score
            both_low = best_dev in LOW_POWER_DEVICES and second_dev in LOW_POWER_DEVICES
            if both_low and score_gap < 0.05:
                best_on = self.device_on_frames.get(best_dev, -10**9)
                second_on = self.device_on_frames.get(second_dev, -10**9)
                if second_on > best_on:
                    logging.info(
                        f"[OFF LIFO TIE-BREAK] {best_dev}(s={best_score:.2f}) vs "
                        f"{second_dev}(s={second_score:.2f}); gap={score_gap:.2f} < 0.05, "
                        f"both low-power → LIFO: {second_dev} (more recent ON: "
                        f"frame {second_on} > {best_on})"
                    )
                    best_dev, best_score = second_dev, second_score

        if guarded:
            logging.info("[LOW-POWER OFF GUARD] protected=" + ", ".join([f"{d}({r})" for d, r in guarded]))

        if best_score > 1.10:
            self._off_reject_reason = "low_score"
            return None, best_score

        # v12: partial drop reject.
        # 다중 active 상태에서 작은 sig 가전이 partial drop 에 더 가깝게 score 가 나오는 문제 방어.
        # 예: charger sig=1130, tv sig=1545. TV unplug 초기 drop_h1=475 일 때
        #     score(charger)=0.57 < score(tv)=0.66 → charger 가 선택되지만 실제는 TV partial drop.
        # 선택된 가전의 sig 의 55% 미만으로 drop 했으면 OFF 확정하지 않고 누적 대기.
        sig_for_best = self.device_signatures.get(best_dev, {})
        sig_best_h1 = abs(float(sig_for_best.get("delta_h1", 0.0)))
        # v61: LP device 한정 임계 0.55 → 0.40 (line 1846 와 동일 사유). HP 는 0.55 유지.
        partial_threshold = 0.40 if best_dev in LOW_POWER_DEVICES else 0.55
        if sig_best_h1 > 0 and drop_h1 < sig_best_h1 * partial_threshold:
            logging.info(
                f"[OFF PARTIAL REJECT] {best_dev} drop_H1={drop_h1:.1f} < "
                f"{int(partial_threshold*100)}% of sig_H1={sig_best_h1:.1f}; "
                f"누적 대기 (baseline frozen)"
            )
            self._off_reject_reason = "partial"
            return None, float("inf")

        # v14: multi-active general path 에서도 over-sized drop reject.
        # 실측: dryer OFF 후 active=[charger, tv] 상태에서 dryer drain 잔향 drop_h1=13304 가
        # tv (sig=1559) 에 score 상 가까워 보여 multi-active 일반 signature matching 에서 tv OFF 채택됨.
        # high-power residue guard 28 프레임이 지났더라도 drain 은 더 길게 이어지므로 sig 의 2배 초과
        # 이거나 절대 1500 초과면 high-power 잔향으로 보고 reject 한다.
        if best_dev in LOW_POWER_DEVICES and drop_h1 > max(sig_best_h1 * 2.0, 1500.0):
            logging.info(
                f"[OFF OVERSIZED REJECT] {best_dev} multi drop_H1={drop_h1:.1f} > "
                f"max(2*sig_H1={sig_best_h1*2:.1f}, 1500); high-power drain 잔향"
            )
            self._off_reject_reason = "oversized"
            return None, float("inf")

        return best_dev, best_score

    # ------------------------------------------------------------------
    # Baseline / Reclassify / Sanity
    # ------------------------------------------------------------------
    def _sync_baseline_to(self, win_feat):
        self.baseline_feat = dict(win_feat)
        self.baseline_irms = float(win_feat.get("Irms_adc_mean", self.baseline_irms))
        self.baseline_h1 = float(win_feat.get("H1_60_mag_mean", self.baseline_h1))

    def _update_baseline(self, win_feat):
        if self.pending_on is not None:
            return

        d_irms = float(win_feat.get("Irms_adc_mean", 0.0)) - self.baseline_irms
        d_h1 = float(win_feat.get("H1_60_mag_mean", 0.0)) - self.baseline_h1
        is_stable = abs(d_irms) < IRMS_NOISE_FLOOR and abs(d_h1) < H1_DEVICE_MIN * 0.5

        if self.event_cooldown > 0:
            # v12: partial-drop OFF REJECT 직후엔 baseline 동결.
            # 흡수해버리면 다음 frame d_h1 이 0 근처가 되어 누적된 drop 으로
            # TV OFF 를 잡지 못한다.
            if not self._pending_off_drop:
                self._sync_baseline_to(win_feat)
        else:
            # 쿨다운 만료 → 누적 대기 상태 해제
            if self._pending_off_drop:
                self._pending_off_drop = False
            a = EMA_ALPHA if is_stable else EMA_ALPHA * 0.03
            for k, v in win_feat.items():
                if k in self.baseline_feat:
                    self.baseline_feat[k] = (1 - a) * self.baseline_feat[k] + a * v
            self.baseline_irms = float(self.baseline_feat.get("Irms_adc_mean", self.baseline_irms))
            self.baseline_h1 = float(self.baseline_feat.get("H1_60_mag_mean", self.baseline_h1))

        if not self.active_devices:
            self.idle_baseline_irms = self.baseline_irms
            self.idle_baseline_h1 = self.baseline_h1

        if len(self.active_devices) >= 2:
            self._sanity_check_active_devices(win_feat)

        if self.reclassify_countdown > 0 and self.active_devices:
            self.reclassify_countdown -= 1
            if self.reclassify_countdown == 0:
                self._reclassify_latest_signature(win_feat)

        # v46: HP OFF 후 30 frames 뒤 active LP 검증
        if (self._hp_off_lp_cleanup_frame > 0
                and self.frame_count >= self._hp_off_lp_cleanup_frame
                and self.event_cooldown == 0):
            self._hp_off_lp_cleanup_frame = 0
            self._cleanup_lp_after_hp_off(win_feat)

    def _cleanup_lp_after_hp_off(self, win_feat):
        """HP OFF 후 baseline 안정화 시점에 active LP 의 실제 존재 검증.

        microwave 같은 HP 가 active 일 때 charger/tv 가 빠져도 H1 변화가 노이즈에 묻혀
        cascade force off 가 안 됨. HP OFF 후 baseline 에 LP 의 sig 가 안 보이면
        실제로 빠진 것으로 판단해 cleanup.
        """
        if not self.active_devices or self.idle_baseline_h1 <= 0:
            return

        current_h1 = self.baseline_h1
        excess = current_h1 - self.idle_baseline_h1

        active_lp = [d for d in self.active_devices if d in LOW_POWER_DEVICES]
        if not active_lp:
            return

        total_lp_sig = sum(
            abs(float(self.device_signatures.get(d, {}).get("delta_h1", 0.0)))
            for d in active_lp
        )
        if total_lp_sig <= 0:
            return

        ratio = excess / total_lp_sig

        logging.info(
            f"[HP-OFF LP-CLEANUP CHECK] baseline_h1={current_h1:.1f}, idle={self.idle_baseline_h1:.1f}, "
            f"excess={excess:.1f}, active LP sig 합={total_lp_sig:.1f}, ratio={ratio:.2f}"
        )

        # v52f: partial 매칭 우선 시도.
        # 기존 로직은 ratio < 0.50 이면 무조건 모든 LP force off → 사용자가 한 LP 만 뺐는데도
        # sig 가 multi-device 등록 시점 noise 로 부풀려져 ratio 가 낮게 나오면 나머지 LP 까지
        # 잘못 OFF 되는 cascade 발생.
        # 실측 (2026-05-27 16:12:54): tv (sig=1648) + charger (sig=2038) active 중 사용자가
        # charger 만 뽑음. baseline excess=1275.9, total_lp_sig=3687.2, ratio=0.35 → 기존
        # 로직은 ratio<0.50 분기로 tv 까지 force off.
        # 매치 검증: charger 빠진 거라면 expected_remaining = 3687-2038 = 1648, ratio_after =
        # 1275.9/1648 = 0.77 → 1.0 근처. partial 매치 ✓ → charger 만 OFF 하면 정확.
        # 따라서 항상 partial 매칭부터 시도. 매치 실패하고 ratio 가 매우 낮을 때 (< 0.30) 만
        # 전체 OFF — 확실히 모두 빠진 케이스 (excess ≈ 0) 보호.
        if len(active_lp) >= 2:
            best_match = None
            best_diff = float("inf")
            best_ratio_after = 0.0
            for dev in active_lp:
                dev_sig = abs(float(self.device_signatures.get(dev, {}).get("delta_h1", 0.0)))
                expected_remaining = total_lp_sig - dev_sig
                if expected_remaining <= 0:
                    continue
                ratio_after = excess / expected_remaining
                diff = abs(ratio_after - 1.0)
                # 0.5 ~ 1.8 = 다른 LP sig 가 baseline 으로 설명 가능한 범위 (±50% 노이즈 허용)
                if 0.5 <= ratio_after <= 1.8 and diff < best_diff:
                    best_diff = diff
                    best_match = dev
                    best_ratio_after = ratio_after
            if best_match is not None:
                # v72: PARTIAL force off 자체 비활성화. _force_device_off 가 OFF VERIFY
                # callback (orchestrator 의 relay 토글 검증) 을 거치지 않고 바로 force off
                # 하므로, baseline 측정만으로 어느 LP 가 빠졌는지 모호한 경우 (두 LP sig 가
                # 비슷한 영역) 잘못된 force off 발생.
                # 실측 (2026-05-29 20:18:00): cleaner OFF 직후 사용자 tv pull → baseline
                # 1370 (charger 만 남은 상태). 그런데 charger sig=715, tv sig=1267 합 1982.
                # ratio_after_for_charger = 1296/1267 = 1.02 (1.0 에 가까움) → AI 가
                # "charger 가 빠졌다" 잘못 판단 → charger force off ❌ (실은 tv 빠짐)
                # → 일반 OFF cascade (누적 drop 매칭) 로 위임 → 정확한 dev sig 매칭 후 OFF
                # VERIFY 거쳐 force off.
                logging.info(
                    f"[HP-OFF LP-CLEANUP PARTIAL SKIP] {best_match} 후보 ratio_after="
                    f"{best_ratio_after:.2f} 이지만 baseline 모호 가능성 → "
                    f"force off 보류, 일반 cascade 위임 (OFF VERIFY 검증 거치도록)"
                )
                return

        # partial 매치 실패. 진짜로 모두 빠진 (excess ≈ 0) 경우만 전체 force off.
        # 0.30 임계: tv 단독 (sig=1648) active 중 빠진 케이스 excess ≈ 0 ~ 노이즈,
        # ratio ≈ 0. charger 단독 active 중 빠진 케이스도 동일.
        if ratio < 0.30:
            for dev in list(active_lp):
                logging.info(f"[HP-OFF LP-CLEANUP] {dev} 모두 빠진 것으로 판단 → force off (ratio={ratio:.2f} < 0.30)")
                self._force_device_off(dev)
        else:
            logging.info(
                f"[HP-OFF LP-CLEANUP SKIP] ratio={ratio:.2f} 애매 (partial 매치 실패, 전체 OFF 임계 미달); "
                f"baseline drift 가능성, 일반 OFF event 처리에 위임"
            )

    def _reclassify_latest_signature(self, win_feat):
        if not self.active_devices or not self.pre_event_baseline_feat:
            return
        dev_name = list(self.active_devices.keys())[-1]
        # v94: LP(charger/tv)는 RECLASSIFY 로 sig 를 키우지 않는다. LP OFF 는 점진적
        # ramp-down 이라 steady-state sig (실측 charger ON 767 → RECLASSIFY 1200.8) 로
        # 키우면 OFF drop 이 sig*0.80 (=960) 에 도달 못해 LP MATCH 실패 → high-power
        # PARTIAL 로 매 frame reject → 모든 HP 빠진 뒤 cleanup 으로 26초 늦게 force off
        # (2026-05-31 03:01:17~03:02:22). ON 시점 sig 가 LP OFF drop 과 더 잘 맞음.
        if dev_name in LOW_POWER_DEVICES:
            return
        new_d_irms = float(win_feat.get("Irms_adc_mean", 0.0)) - self.pre_event_baseline_irms
        new_d_h1 = float(win_feat.get("H1_60_mag_mean", 0.0)) - self.pre_event_baseline_h1
        new_d_pabs = float(win_feat.get("Pabs_mean_proxy_mean", win_feat.get("Pabs_mean_proxy", 0.0))) - float(self.pre_event_baseline_feat.get("Pabs_mean_proxy_mean", self.pre_event_baseline_feat.get("Pabs_mean_proxy", 0.0)))

        old = self.device_signatures.get(dev_name, {})
        if abs(new_d_h1) > abs(float(old.get("delta_h1", 0.0))) * 1.10:
            # v42: 부호 변경 reclassify 방어 (tv toggle-id 중 H1 음수 저장 → 잘못된 sig).
            # LP 비정상 크기 방어(구 too_big_for_lp)는 위 v94 LP skip 이 대신한다.
            old_d_h1 = float(old.get("delta_h1", 0.0))
            sign_flip = (old_d_h1 != 0 and new_d_h1 * old_d_h1 < 0)
            if sign_flip:
                logging.info(
                    f"[RECLASSIFY SKIP] '{dev_name}' sign_flip new dH1={new_d_h1:.1f} "
                    f"(old={old_d_h1:.1f}) - reclassify 무시"
                )
                return
            self.device_signatures[dev_name] = {
                "delta_irms": new_d_irms,
                "delta_h1": new_d_h1,
                "delta_pabs": new_d_pabs,
                "method": "reclassify_signature_update",
            }
            logging.info(
                f"[RECLASSIFY] '{dev_name}' signature update dI={new_d_irms:.1f}, dH1={new_d_h1:.1f}, dPabs={new_d_pabs:.1f}"
            )

    def _sanity_check_active_devices(self, win_feat):
        if self.event_cooldown > 0 or not self.device_signatures:
            return

        h1_now = float(win_feat.get("H1_60_mag_mean", 0.0))
        total_delta_h1 = sum(float(sig.get("delta_h1", 0.0)) for sig in self.device_signatures.values())
        expected_all = self.idle_baseline_h1 + total_delta_h1

        for dev_name in list(self.active_devices.keys()):
            # v6: charger/tv는 H1 기여가 작고 ramp가 길어서 high-power 기기 투입 중
            # sanity check로 잘못 OFF되는 경우가 많다. 명시적 OFF 이벤트로만 끈다.
            if dev_name in LOW_POWER_DEVICES:
                continue
            sig = self.device_signatures.get(dev_name, {})
            dev_h1 = abs(float(sig.get("delta_h1", 0.0)))
            if dev_h1 < SANITY_CHECK_H1_MIN:
                continue
            expected_without = expected_all - dev_h1
            diff_with = abs(h1_now - expected_all)
            diff_without = abs(h1_now - expected_without)
            if diff_without < diff_with * 0.25 and diff_with > H1_DEVICE_MIN * 8:
                logging.info(
                    f"[SANITY-OFF] {dev_name} H1 contribution disappeared "
                    f"(h1_now={h1_now:.0f}, expected_all={expected_all:.0f}, expected_without={expected_without:.0f})"
                )
                self._force_device_off(dev_name)
                break

    def _force_device_off(self, dev_name):
        sk_idx = self.active_devices.get(dev_name)
        if sk_idx is None:
            return
        target_sk = next((s for s in self.sockets if s.idx == sk_idx), None)
        if target_sk is None:
            return
        target_sk.turn_off()
        del self.active_devices[dev_name]
        # v29: sig 를 history 에 백업
        sig_to_save = self.device_signatures.pop(dev_name, None)
        if sig_to_save is not None:
            self._backup_signature(dev_name, sig_to_save)
        self.device_on_frames.pop(dev_name, None)
        self.device_on_wallclock.pop(dev_name, None)
        if dev_name in HIGH_POWER_DEVICES:
            self.last_high_power_off_frame = self.frame_count
            # v46: HP OFF 후 30 frames 뒤 active LP 검증
            if any(d in LOW_POWER_DEVICES for d in self.active_devices):
                self._hp_off_lp_cleanup_frame = self.frame_count + 30
        self.event_cooldown = EVENT_COOLDOWN_FRAMES
        self.event_history.append((self.frame_count, "OFF", dev_name))
        logging.info(f"[FORCE OFF] Socket{target_sk.idx} ({dev_name}) by H1 sanity check")

    def _backup_signature(self, dev_name, sig):
        """v29: OFF 시 sig 를 history 에 백업. 같은 라벨 재등록 시 dominance 로 작게 측정되면 백업 사용."""
        existing = self.device_signatures_history.get(dev_name, {})
        existing_h1 = abs(float(existing.get("delta_h1", 0.0)))
        new_h1 = abs(float(sig.get("delta_h1", 0.0)))
        # 더 큰 |dH1| 만 유지 (작은 측정은 dominance 영향일 수 있음)
        if new_h1 > existing_h1:
            self.device_signatures_history[dev_name] = dict(sig)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------
    def _make_status(self, event, win_feat):
        return {
            "frame_count": self.frame_count,
            "event": event,
            "win_feat": win_feat,
            "baseline_irms": self.baseline_irms,
            "baseline_h1": self.baseline_h1,
            "sockets": [s.to_dict() for s in self.sockets],
            "active_devices": dict(self.active_devices),
            "event_cooldown": self.event_cooldown,
            "pending_on": self.pending_on is not None,
            "fs_actual": self._last_fs,
            "ch0": self._last_ch0,
            "ch1": self._last_ch1,
        }
