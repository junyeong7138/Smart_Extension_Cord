#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_engine_v2.py
===============

WattsUp NILM Multi-tap 추론 엔진 v2 (OFF 재구성판).

설계 핵심 (ai_extension_v3 대비)
-------------------------------
ON 감지/분류 로직은 v3(=v52j)에서 *그대로* 이식해 검증된 동작을 보존한다.
**OFF 결정 로직 (signature 매칭 추측, _select_off_device_by_signature 651줄 +
_handle_device_off cascade 406줄) 은 통째로 제거**한다.

이유: 작은 LP기기(charger sig_h1≈650, tv≈1400)를 큰 HP기기(dryer≈18000,
cleaner≈6500)와 동시에 켠 상태에서 LP를 뽑으면, 그 작은 H1 변화가 HP duty
노이즈에 묻혀 signature 추측이 후보 선정부터 실패한다. v79~v82 의 가드 땜질이
모두 이 추측 단계에서 막혔다.

새 OFF 흐름 (책임 이동)
-----------------------
- AIEngine 은 OFF 를 *결정하지 않는다*. 매 frame "전체 H1 이 active 기기 sig 합의
  기대치보다 의미있게 부족한가" 만 보고 `off_suspect` flag 를 세운다.
- 실제 OFF 결정은 socket_orchestrator_v2 가 한다: off_suspect 가 뜨면 ASSIGNED
  소켓을 하나씩 릴레이 OFF → ΔH1 측정 → 부재(ratio_h1<0.30)면 그 기기 OFF 확정.
  릴레이 토글이 *물리적 진실* 이라 추측이 필요 없다.
- orchestrator 가 부재 확정 시 `engine.confirm_device_off(dev)` 를 호출해야만
  active_devices 에서 제거된다. **AIEngine 은 active_devices 에 ON 만 추가하고
  절대 스스로 OFF 로 빼지 않는다.**

주의
----
- CT/PT가 전체 1개라면 실제 물리 소켓 번호를 맞추는 코드는 아니다.
- Socket 1~4는 UI 표시 슬롯이다 (실제 물리 매핑은 orchestrator 가 가진다).
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

AI_VERSION = "ai_engine_v2_2026_05_31_off_fullscan_by_orchestrator"

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

# v2 OFF-suspect 트리거 (orchestrator 전수 스캔 위임용).
# "현재 H1 이 baseline 대비 의미있게 하락" → 뭔가 꺼졌을 가능성.
# 어느 기기인지는 추측 안 함 (orchestrator 가 릴레이 토글로 결정).
#
# baseline 대비를 쓰는 이유 (sig 합 기대치 대신):
# - charger/tv 는 ramp 가 길어 등록 시점 sig 가 과소측정되고 이후 상승분은 baseline EMA 만
#   흡수한다. 그래서 idle+Σsig 기대치가 실제 H1 보다 1000+ 낮게 나와, 작은 LP OFF 의
#   shortfall 이 음수가 되어 영영 트리거 못 한다 (실측 2026-05-31 02:29~30: charger/tv
#   뽑았는데 dryer 끌 때까지 47초간 미감지). baseline_h1 은 직전 실제 H1 이라 누적 오차 없음.
# - off_suspect 중에는 _update_baseline 이 freeze 하므로 EMA 가 하락을 흡수하기 전에 잡힌다.
OFF_SUSPECT_ABS_H1 = 400.0   # 안정 noise(±130) 보다 크고 charger sig(~788) 보다 작게
OFF_SUSPECT_CONSEC = 2       # 연속 N frame 유지돼야 trigger (단발 dip 무시)

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
        self.device_on_frames = {}
        # v52d: LP RAMP CONTINUATION 의 elapsed 판정용 wall-clock 기록.
        # frame_count 는 SPI 부하로 fs 변동이 커서 시간 환산 부정확.
        self.device_on_wallclock = {}

        self._last_ch0 = np.zeros(buffer_size)
        self._last_ch1 = np.zeros(buffer_size)
        self._last_fs = 0.0

        # v2: OFF 의심 신호 (orchestrator 전수 스캔 트리거).
        # AIEngine 은 OFF 를 결정하지 않고 "뭔가 꺼진 것 같다" 만 알린다.
        # off_suspect=True 이면 orchestrator monitor 가 ASSIGNED 소켓 전수 토글로
        # 어느 기기가 빠졌는지 물리적으로 확정한다.
        self.off_suspect = False
        self.off_suspect_drop_h1 = 0.0
        self._off_suspect_consec = 0

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
        else:
            # v2: OFF 는 여기서 결정하지 않는다. "전체 H1 부족" 의심만 세우고
            # orchestrator 전수 스캔에 위임. IDLE 이면 baseline EMA 갱신.
            self._update_off_suspect(win_feat)
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
            # v2: OFF 판정은 _classify_event 가 하지 않는다. _update_off_suspect 가
            # "active sig 합 대비 전체 H1 부족" 으로 의심만 세우고, orchestrator 전수
            # 스캔이 어느 기기인지 물리적으로 확정한다. 여기선 ON 만 검출.

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

    # ------------------------------------------------------------------
    # OFF 의심 신호 (v2) — 결정은 orchestrator 전수 스캔이 한다
    # ------------------------------------------------------------------
    def _update_off_suspect(self, win_feat):
        """현재 H1 이 baseline 대비 의미있게 하락하면 off_suspect.

        baseline_h1 은 직전 안정 상태의 실제 H1 이라 누적 오차가 없다 (sig 합 기대치는
        charger/tv ramp 과소측정으로 1000+ 어긋나 작은 LP OFF 를 놓침 — v2 첫 실측 실패).
        off_suspect 가 서면 _update_baseline 이 freeze 하므로 EMA 가 하락을 흡수하기 전에
        잡힌다.

        어느 기기가 빠졌는지는 *추측하지 않는다*. orchestrator 가 off_suspect 를
        보고 ASSIGNED 소켓을 전수 토글해 물리적으로 확정한다.
        """
        if self.event_cooldown > 0 or not self.active_devices:
            self.off_suspect = False
            self._off_suspect_consec = 0
            return

        current_h1 = float(win_feat.get("H1_60_mag_mean", 0.0))
        # baseline 대비 하락량. baseline 은 직전 ON 등록/안정 시점의 실제 H1.
        drop = self.baseline_h1 - current_h1

        if drop > OFF_SUSPECT_ABS_H1:
            self._off_suspect_consec += 1
            if self._off_suspect_consec >= OFF_SUSPECT_CONSEC:
                if not self.off_suspect:
                    logging.info(
                        f"[OFF-SUSPECT] H1 drop={drop:.1f} > {OFF_SUSPECT_ABS_H1:.0f} "
                        f"(baseline_h1={self.baseline_h1:.1f}, current_h1={current_h1:.1f}, "
                        f"active={list(self.active_devices)}) → orchestrator 전수 스캔 위임"
                    )
                self.off_suspect = True
                self.off_suspect_drop_h1 = drop
        else:
            self._off_suspect_consec = 0
            # off_suspect flag 는 orchestrator 가 스캔 처리 후 직접 리셋한다.

    def confirm_device_off(self, dev, win_feat=None):
        """orchestrator 전수 스캔이 부재 확정한 dev 를 active 에서 제거 + baseline 재동기화.

        AIEngine 이 active_devices 에서 기기를 빼는 *유일한* 경로.
        """
        sig = self.device_signatures.pop(dev, None)
        if sig is not None:
            self._backup_signature(dev, sig)
        sk_idx = self.active_devices.pop(dev, None)
        if sk_idx is not None:
            target_sk = next((s for s in self.sockets if s.idx == sk_idx), None)
            if target_sk is not None:
                target_sk.turn_off()
        self.device_on_frames.pop(dev, None)
        self.device_on_wallclock.pop(dev, None)
        if dev in HIGH_POWER_DEVICES:
            self.last_high_power_off_frame = self.frame_count

        # baseline 재동기화: 현재 측정값으로. 남은 active 기기 sig 합은 그대로 두고
        # idle 기준만 다시 잡는다. win_feat 없으면 _latest_win_feat 사용.
        wf = win_feat or getattr(self, "_latest_win_feat", None)
        if wf:
            self._sync_baseline_to(wf)
            if not self.active_devices:
                self.idle_baseline_irms = self.baseline_irms
                self.idle_baseline_h1 = self.baseline_h1

        self.reclassify_countdown = 0
        self.event_cooldown = EVENT_COOLDOWN_FRAMES
        self.off_suspect = False
        self._off_suspect_consec = 0
        self.event_history.append((self.frame_count, "OFF", dev))
        logging.info(f"[DEVICE OFF] {dev} confirmed by orchestrator full-scan (socket idx={sk_idx})")

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

        # v26→v2: PENDING ON 트리거 시점엔 cond2 ON (d_h1 양수) 이었지만 8 프레임 정착 후
        # d_h1 가 명백히 음수이면 transient ON 트리거였음 (실제론 뭔가 빠지는 진동).
        # v2 에선 OFF 를 여기서 처리하지 않는다. 등록을 폐기하고 baseline 을 현재값으로
        # 동기화한 뒤 종료 → 다음 frame 에서 _update_off_suspect 가 H1 부족을 감지해
        # orchestrator 전수 스캔으로 위임한다.
        d_h1_check = float(win_feat.get("H1_60_mag_mean", 0.0)) - pre_h1
        d_irms_check = float(win_feat.get("Irms_adc_mean", 0.0)) - pre_irms
        if d_h1_check < -100.0:
            logging.info(
                f"[PENDING ON → ABORT] 정착 d_irms={d_irms_check:.1f}, d_h1={d_h1_check:.1f} 음수 → "
                f"transient ON, 등록 폐기 (OFF 는 off_suspect 가 처리)"
            )
            self._sync_baseline_to(win_feat)
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
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

        if device is None:
            logging.warning(
                f"[DEVICE ON REJECT] unknown | reason={reason}, dI={d_irms:.1f}, dH1={d_h1:.1f}, dPabs={d_pabs:.1f}, details={details}"
            )
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
                    cum_d_pf = (
                        float(old_sig.get("delta_pf", 0.0))
                        + float(win_feat.get("PF_proxy_mean", 0.0))
                        - float(pre_feat.get("PF_proxy_mean", 0.0))
                    )
                    self.device_signatures[device] = {
                        "delta_irms": cum_d_irms,
                        "delta_h1": cum_d_h1,
                        "delta_pabs": cum_d_pabs,
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
                # v53 (2026-05-30 19:45:33 log 기반): charger 자체 재트리거/노이즈를
                # "두 번째 LP = tv" 로 환각하는 것 방지.
                # 실측: charger 단독 active 중 charger 자신의 작은 변동 (d_irms=6.4,
                # d_h1=228.8) 이 cond2 ON 트리거 → RF abs charger:1.00 (tv:0.003) 인데
                # 이 분기가 d_h1=469.6 ≥ 450 만 보고 무조건 alt=tv 채택 → 유령 tv ON
                # @socket4. 직후 충전기 unplug 시 그 유령 tv 가 먼저 force-off 되는 cascade.
                # d_h1 (charger H1 영역 364~499 와 겹침) 만으로는 charger 자체 변동을 못 거른다.
                # 진짜 새 tv 면 절대 신호에 tv 고조파가 더해져 RF abs[tv] 가 의미있게 오르므로,
                # RF abs 가 tv 를 임계 (0.15) 이상 지목할 때만 alt=tv 채택.
                #
                # v54 (2026-05-30 19:56:45 log 기반): 단, HP (cleaner/dryer/microwave) 가
                # active 면 그 거대 전류가 절대 신호를 지배해 RF abs[tv] 가 진짜 tv 여도 0 으로
                # 묻힌다 (실측: cleaner+dryer+charger active 중 사용자가 TV 꽂음 → d_h1=810.6
                # 진짜 tv 신호인데 probs_abs={dryer:0.80, tv:0.0} → v53 가드가 오판해서 TV 가
                # 끝까지 PENDING 으로 남음). 따라서 RF abs 교차검증은 HP 가 active 가 아닐 때만
                # 적용 (그때만 abs[tv] 가 신뢰 가능). HP active 중엔 기존대로 신호 (d_h1) 기반
                # alt=tv. v53 가 막으려던 유령 tv 는 charger 단독 (HP 없음) 케이스였으므로 그대로
                # 차단된다.
                hp_active = any(d in self.active_devices for d in HIGH_POWER_DEVICES)
                if hp_active:
                    alt = "tv"
                elif self._strong_inactive_abs_candidate(
                        win_feat, d_irms, d_h1, exclude=device, threshold=0.15) == "tv":
                    alt = "tv"
                else:
                    logging.info(
                        f"[ALT TV REJECT] charger active 중 (HP 없음) d_h1={d_h1:.1f} 이벤트지만 "
                        f"RF abs 가 tv 를 지목 안 함 (charger 자체 변동/노이즈 추정) → "
                        f"alt=tv 보류, 일반 fallback 위임"
                    )
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
                # 드라이기/전자레인지/청소기 모드 변경처럼 같은 기기 출력만 변한 경우
                logging.info(f"[ON MODE UPDATE] {device} already active, treat as mode/power update")
                if device in HIGH_POWER_DEVICES:
                    self.last_high_power_event_frame = self.frame_count
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
        self.off_suspect = False  # v2: 새 ON event → OFF 의심 리셋
        self._off_suspect_consec = 0
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
        if low_power_region:
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

        # v2: off_suspect 중에는 baseline 동결. EMA 가 H1 부족분을 흡수해버리면
        # expected-current 차이가 사라져 의심이 풀리고 orchestrator 스캔 전에
        # OFF 신호가 묻힌다. 스캔이 끝나 confirm_device_off 가 baseline 을 resync
        # 하거나, 의심이 자연 해소(_off_suspect_consec=0)될 때까지 freeze.
        if self.off_suspect:
            return

        if self.event_cooldown > 0:
            self._sync_baseline_to(win_feat)
        else:
            a = EMA_ALPHA if is_stable else EMA_ALPHA * 0.03
            for k, v in win_feat.items():
                if k in self.baseline_feat:
                    self.baseline_feat[k] = (1 - a) * self.baseline_feat[k] + a * v
            self.baseline_irms = float(self.baseline_feat.get("Irms_adc_mean", self.baseline_irms))
            self.baseline_h1 = float(self.baseline_feat.get("H1_60_mag_mean", self.baseline_h1))

        if not self.active_devices:
            self.idle_baseline_irms = self.baseline_irms
            self.idle_baseline_h1 = self.baseline_h1

        if self.reclassify_countdown > 0 and self.active_devices:
            self.reclassify_countdown -= 1
            if self.reclassify_countdown == 0:
                self._reclassify_latest_signature(win_feat)

    def _reclassify_latest_signature(self, win_feat):
        if not self.active_devices or not self.pre_event_baseline_feat:
            return
        dev_name = list(self.active_devices.keys())[-1]
        new_d_irms = float(win_feat.get("Irms_adc_mean", 0.0)) - self.pre_event_baseline_irms
        new_d_h1 = float(win_feat.get("H1_60_mag_mean", 0.0)) - self.pre_event_baseline_h1
        new_d_pabs = float(win_feat.get("Pabs_mean_proxy_mean", win_feat.get("Pabs_mean_proxy", 0.0))) - float(self.pre_event_baseline_feat.get("Pabs_mean_proxy_mean", self.pre_event_baseline_feat.get("Pabs_mean_proxy", 0.0)))

        old = self.device_signatures.get(dev_name, {})
        if abs(new_d_h1) > abs(float(old.get("delta_h1", 0.0))) * 1.10:
            # v42: 부호 변경 / LOW_POWER 비정상 크기 reclassify 방어.
            # 실측 (2026-05-24 18:45:07): tv ON 직후 ORCH toggle-id 중 H1 일시 감소로
            # tv sig 가 dH1=-3136 (음수, 원래 +1573) 으로 저장됨. 후속 HP PARTIAL HOLD
            # 가 tv sig_abs=3136>3000 으로 잡아 charger force OFF 를 막아버렸다.
            old_d_h1 = float(old.get("delta_h1", 0.0))
            sign_flip = (old_d_h1 != 0 and new_d_h1 * old_d_h1 < 0)
            too_big_for_lp = (dev_name in LOW_POWER_DEVICES and abs(new_d_h1) > 2500.0)
            if sign_flip or too_big_for_lp:
                logging.info(
                    f"[RECLASSIFY SKIP] '{dev_name}' new dH1={new_d_h1:.1f} (old={old_d_h1:.1f}) "
                    f"sign_flip={sign_flip} too_big_lp={too_big_for_lp} - reclassify 무시"
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
