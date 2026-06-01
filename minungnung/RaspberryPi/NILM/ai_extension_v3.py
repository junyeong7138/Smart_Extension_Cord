#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_extension_v3.py
==================
NILM Multi-tap 추론 엔진 (v3).

v2 대비 변경
------------
1) Spark 기반 plug_in/plug_out 로직 제거
   - 어차피 wired plug-in spark 는 안정적으로 감지 불가
   - 소켓 매핑은 추후 relay 모듈로 처리 예정
2) SocketFSM 단순화: EMPTY <-> DEVICE_ON <-> DEVICE_OFF (3-state)
3) 가전별 실제 전력 하드코딩 -> UI 에 W 단위 표기
4) UI 통합: 4 소켓 + 오실로스코프 + 디버그 정보 (한 화면)
5) 이모지 / 유니코드 심볼 제거 (라파 모니터 호환)

데이터 흐름
-----------
spi -> DSPEngine.process_raw_mode -> frame_feature -> window_feature
                                                       |
                                                       v
                                       _classify_event()  [DEVICE_ON / DEVICE_OFF / IDLE]
                                                       |
                                              +--------+--------+
                                          ON/OFF              IDLE
                                              |                |
                                       _identify_device   _update_baseline
                                              |
                                       _socket_handle_*()

소켓 FSM (v3 단순화)
--------------------
    EMPTY  --DEVICE_ON--> DEVICE_ON  <--DEVICE_ON-- DEVICE_OFF
                              |                          ^
                              +-------DEVICE_OFF---------+
"""

import os
import json
import logging
import datetime
import threading
from collections import deque

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import joblib

from dsp_engine import DSPEngine
from feature_extractor import (
    extract_frame_features,
    aggregate_window_features,
    WINDOW_SIZE,
)

# =====================================================================
# 경로 / 상수
# =====================================================================

def find_model_dir():
    """
    Model 폴더를 유연하게 찾기.
    여러 위치를 탐색해서 rf_device_classifier.joblib 이 있는 곳을 반환.
    """
    base = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()
    paths = [
        os.path.join(base, "Model"),
        os.path.join(base, "..", "Model"),
        os.path.join(base, "..", "..", "Model"),
        os.path.join(cwd, "Model"),
        os.path.join(cwd, "..", "Model"),
        os.path.join(cwd, "..", "..", "Model")
    ]
    for p in paths:
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "rf_device_classifier.joblib")):
            return p
    # 못 찾으면 기본 경로 반환 (에러는 모델 로드 시점에서 발생)
    return os.path.join(base, "..", "Model")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = find_model_dir()
MODEL_PATH = os.path.join(MODEL_DIR, "rf_device_classifier.joblib")
FEATURES_PATH = os.path.join(MODEL_DIR, "rf_device_features.json")

N_SOCKETS = 4

# ---- 이벤트 판정 임계값 (Irms_adc 기준) ----
IRMS_NOISE_FLOOR = 3.0      # 이 이하 변화는 노이즈
IRMS_DEVICE_MIN = 6.0       # 가전 ON/OFF 시 Irms 최소 변화
H1_DEVICE_MIN = 40.0        # 가전 ON/OFF 시 H1 최소 변화 (실 H/W charger/fan H1 < 학습값 보정)
IRMS_RESISTIVE_MIN = 15.0   # H1 작은 부하(저전력 charger 등) 검출용 Irms-only 임계
SANITY_CHECK_H1_MIN = 500.0 # sanity check 참여 최소 H1 기여 (이하는 측정 노이즈에 묻혀 신뢰 불가)

# ---- 쿨다운 (frame 단위) ----
EVENT_COOLDOWN_FRAMES = 12  # 이벤트 발생 후 N frame 동안 새 이벤트 무시 (기동 과도전류 방어)

# ---- Baseline EMA ----
EMA_ALPHA = 0.2

# ---- Window 큐 ----
FRAME_QUEUE_SIZE = WINDOW_SIZE
MIN_FRAMES_FOR_DECISION = WINDOW_SIZE

# ---- RF 신뢰도 ----
# 0.50 → 0.55: 경계값(0.50) 통과로 인한 오분류 방지
# 0.55 미만이면 range_match(Irms+H1 범위 페널티) fallback
RF_CONFIDENCE_THRESHOLD = 0.55

# ---- PT/CT 센서 기반 실시간 전력 계산 상수 ----
# 아래 값들은 "기기별 고정 전력"이 아니라 센서 보정값이다.
# UI 전력은 매 frame마다 CH0(PT 전압파형), CH1(CT/ACS 전류파형) raw로 계산된다.
ADC_VREF = 3.3
ADC_FULL_SCALE = 4096.0

# 전압 채널은 PT 파형의 모양/위상을 사용하고, RMS 크기는 국내 상용전원 기준으로 정규화한다.
# 실제 계측 전압값을 별도로 보정했다면 USE_NOMINAL_VOLTAGE_RMS=False로 바꾸고
# VOLTAGE_SENSOR_SCALE_V_PER_ADC_V를 맞춰서 사용하면 된다.
USE_NOMINAL_VOLTAGE_RMS = True
MAINS_VRMS_NOMINAL = 220.0
VOLTAGE_SENSOR_SCALE_V_PER_ADC_V = 1.0

# 전류 센서 감도. ACS712-30A는 보통 0.066 V/A, ACS712-20A는 0.100 V/A,
# ACS712-5A는 0.185 V/A이다. 사용하는 모듈에 맞게 이 값만 바꾸면 된다.
CURRENT_SENSOR_SENSITIVITY_V_PER_A = 0.066

# PT/CT 극성이 반대로 연결되어 평균전력이 음수로 나오면 True로 바꾼다.
INVERT_POWER_POLARITY = False

# phase 보정이 완벽하지 않은 센서 환경에서는 음수 부호만 제거해서 표시한다.
USE_ABS_ACTIVE_POWER = True

# real: mean(v*i) 기반 유효전력 W, apparent: Vrms*Irms 기반 피상전력 VA를 W처럼 표시
POWER_DISPLAY_MODE = "real"

POWER_SMOOTH_ALPHA = 0.35
POWER_DISPLAY_DEADBAND_W = 3.0

# ---- charger vs tv 분리 기준 (Irms 거의 겹침 → H1 으로 분리) ----
# 훈련(노트북 charger 재수집 후): charger H1_p90=499 / tv H1_p10=1240 → 중간값.
# 재학습 시 rf_device_features.json 의 class_ranges 를 보고 갱신 필요.
CHARGER_TV_H1_BOUNDARY = 870.0

# ---- 시작 시 기기 감지 (INIT baseline이 높으면 기기가 이미 켜진 것) ----
# 모든 가전 H1 p10 >= 792 (charger 최저). H1 < 300 이면 60Hz 부하 없음 = 센서 DC 오프셋/노이즈.
# Irms 만 보면 센서 baseline(예: Irms≈100, H1≈30)을 가전으로 오탐하므로 H1 임계도 함께 요구.
STARTUP_DEVICE_IRMS_MIN = 30.0
STARTUP_DEVICE_H1_MIN = 300.0

# ---- 재분류 지연 (이벤트 후 steady-state 창으로 재확인) ----
# 기동 과도전류가 섞인 혼합 창 → IDLE 프레임 WINDOW_SIZE개 후 재분류
RECLASSIFY_DELAY = WINDOW_SIZE  # = 10 frames

# ---- 로깅 ----
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
print(f"[LOG FILE] {_LOG_FILE}")


# =====================================================================
# 1. SocketFSM (v3 - 단순화)
# =====================================================================

class SocketFSM:
    """
    하나의 소켓 상태 머신 (v3 단순화).

    State:
      EMPTY        - 가전이 할당 안 됨
      DEVICE_ON    - 가전 인식 후 ON 상태
      DEVICE_OFF   - 가전이 한 번 인식됐다가 OFF 됨 (전력 0)

    Transition:
      EMPTY      -> DEVICE_ON   (DEVICE_ON 이벤트)
      DEVICE_ON  -> DEVICE_OFF  (DEVICE_OFF 이벤트)
      DEVICE_OFF -> DEVICE_ON   (같은 가전 다시 ON)
      DEVICE_OFF -> EMPTY       (UI 리셋 등)
    """

    VALID_STATES = {"EMPTY", "DEVICE_ON", "DEVICE_OFF"}

    def __init__(self, idx):
        self.idx = idx
        self.state = "EMPTY"
        self.device = None
        self.power_w = 0.0
        self.mode = ""

    def assign_device(self, device_name, power_w, mode=""):
        self.device = device_name
        self.state = "DEVICE_ON"
        self.power_w = float(power_w)
        self.mode = mode or ""

    def turn_off(self):
        if self.state == "DEVICE_ON":
            self.state = "DEVICE_OFF"
            self.power_w = 0.0
            self.mode = ""

    def reset_to_empty(self):
        self.state = "EMPTY"
        self.device = None
        self.power_w = 0.0
        self.mode = ""

    def to_dict(self):
        return {
            "idx": self.idx,
            "state": self.state,
            "device": self.device,
            "power_w": self.power_w,
            "mode": self.mode,
        }


# =====================================================================
# 2. AIEngine
# =====================================================================

class AIEngine(DSPEngine):
    """
    NILM 추론 엔진 v3.

    DSPEngine.process_raw_mode 매 호출로 150 sample frame 수집.
    -> frame feature -> window 누적 -> 이벤트 판정 -> 가전 분류 -> 소켓 갱신.
    """

    def __init__(self, spi_core, buffer_size=150):
        super().__init__(spi_core, buffer_size=buffer_size)

        # ---- 모델 ----
        self.model = joblib.load(MODEL_PATH)
        with open(FEATURES_PATH, encoding="utf-8") as f:
            self.info = json.load(f)
        self.feature_names = self.info["feature_names"]
        self.class_ranges = self.info.get("class_ranges", {})

        logging.info(f"Model loaded. classes={list(self.model.classes_)}")
        logging.info(f"Feature count: {len(self.feature_names)}")

        print("\n" + "="*60)
        print("NILM 테스트 프로토콜")
        print("="*60)
        print("중요: 프로그램 시작 시 모든 기기를 뽑아두세요!")
        print("[INIT BASELINE] 메시지 확인 후 아래 순서대로 진행:")
        print("  Step A: 충전기 꽂기(폰 연결 필수). 8초 대기.   → expect charger ON")
        print("  Step B: TV 꽂고 ON.                  8초 대기.  → expect tv ON")
        print("  Step C: 청소기 꽂고 ON.              8초 대기.  → expect cleaner ON")
        print("  Step D: 청소기 OFF.                   8초 대기.  → expect cleaner OFF")
        print("  Step E: 드라이기 꽂고 ON (한 모드).    8초 대기.  → expect dryer ON")
        print("  Step F: 드라이기 OFF.                 8초 대기.  → expect dryer OFF")
        print("  Step G: 전자레인지 꽂고 ON.            8초 대기.  → expect microwave ON")
        print("  Step H: 전자레인지 OFF.                8초 대기.  → expect microwave OFF")
        print("  Step I: TV OFF.                      8초 대기.   → expect tv OFF")
        print("  Step J: 충전기 뽑기.                  5초 대기.   → expect charger OFF")
        print("="*60 + "\n")

        # ---- frame 큐 ----
        self.frame_feats = deque(maxlen=FRAME_QUEUE_SIZE)

        # ---- baseline ----
        self.baseline_feat = None
        self.baseline_irms = 0.0
        self.baseline_h1 = 0.0

        # ---- 아이들(idle) 진짜 베이스라인 (기기가 모두 꺼진 상태) ----
        self.idle_baseline_irms = 0.0
        self.idle_baseline_h1 = 0.0
        self.idle_baseline_pabs = 0.0

        # ---- UI 상태 동시 접근 보호 (matplotlib thread ↔ mobile Flask thread) ----
        self.status_lock = threading.Lock()

        # ---- 기기별 기여값 추적 (멀티 기기 OFF 감지용) ----
        # dev_name -> {"delta_irms": float, "delta_h1": float}
        self.device_signatures = {}

        # ---- 이벤트 직전 베이스라인 (재분류 시 delta 계산용) ----
        self.pre_event_baseline_irms = 0.0
        self.pre_event_baseline_h1 = 0.0
        self.pre_event_baseline_feat = None

        # ---- 재분류 카운트다운 (IDLE 프레임 수) ----
        self.reclassify_countdown = 0

        # ---- 쿨다운 ----
        self.event_cooldown = 0

        # ---- 카운터 ----
        self.frame_count = 0
        self.event_history = deque(maxlen=50)

        # ---- 소켓 ----
        self.sockets = [SocketFSM(i + 1) for i in range(N_SOCKETS)]

        # ---- 현재 켜진 가전 매핑: device_name -> socket_idx ----
        self.active_devices = {}

        # ---- 마지막 raw 신호 (UI 표시용) ----
        self._last_ch0 = np.zeros(buffer_size)
        self._last_ch1 = np.zeros(buffer_size)
        self._last_fs = 0.0

        # ---- PT/CT raw 기반 실시간 전력 상태 ----
        self.latest_total_power_w = 0.0
        self.latest_apparent_power_va = 0.0
        self.latest_vrms_v = 0.0
        self.latest_irms_a = 0.0
        self.latest_power_factor = 0.0

    # ------------------------------------------------------------------
    # 매 frame 처리 (UI 가 주기적으로 호출)
    # ------------------------------------------------------------------
    def process_ai_frame(self):
        """
        한 frame 분 데이터 수집 + NILM 1 step.

        Returns
        -------
        dict (UI 표시용 상태)
        """
        # 1) RAW 수집
        ch0, ch1, ts, fs_actual = self.process_raw_mode()
        self._last_ch0 = ch0
        self._last_ch1 = ch1
        self._last_fs = fs_actual

        # PT/CT raw에서 현재 전체 전력을 매 frame 직접 계산
        self._update_realtime_power_metrics(ch0, ch1)

        # 2) frame feature
        frame_feat = extract_frame_features(ch0, ch1, fs_actual)
        self.frame_feats.append(frame_feat)
        self.frame_count += 1

        # 3) window 안 차면 IDLE
        if len(self.frame_feats) < MIN_FRAMES_FOR_DECISION:
            return self._make_status("WARMUP", None)

        # 4) window aggregation
        win_feat = aggregate_window_features(list(self.frame_feats))

        # 5) 쿨다운 감소
        if self.event_cooldown > 0:
            self.event_cooldown -= 1

        # 6) baseline 초기화
        if self.baseline_feat is None:
            self.baseline_feat = dict(win_feat)
            self.baseline_irms = win_feat["Irms_adc_mean"]
            self.baseline_h1 = win_feat["H1_60_mag_mean"]
            self.baseline_pabs = win_feat.get("Pabs_mean_proxy_mean", 0.0)
            logging.info(f"[INIT BASELINE] Irms={self.baseline_irms:.2f}, "
                         f"H1={self.baseline_h1:.2f}, Pabs={self.baseline_pabs:.2f}")

            if (self.baseline_irms > STARTUP_DEVICE_IRMS_MIN
                    and self.baseline_h1 > STARTUP_DEVICE_H1_MIN):
                # 기기가 이미 켜진 상태로 프로그램 시작됨 → 감지 후 등록
                logging.info(
                    f"[STARTUP] 기기가 이미 ON 상태입니다 (Irms={self.baseline_irms:.2f} > {STARTUP_DEVICE_IRMS_MIN}, "
                    f"H1={self.baseline_h1:.2f} > {STARTUP_DEVICE_H1_MIN}). 시작 시 기기 감지 시도..."
                )
                self._detect_startup_device(win_feat)
            else:
                if self.baseline_irms > STARTUP_DEVICE_IRMS_MIN:
                    logging.info(
                        f"[STARTUP] Irms={self.baseline_irms:.2f} 높지만 H1={self.baseline_h1:.2f} "
                        f"< {STARTUP_DEVICE_H1_MIN} → 센서 idle 노이즈/오프셋으로 처리 (기기 등록 안 함)."
                    )
                self.idle_baseline_irms = self.baseline_irms
                self.idle_baseline_h1 = self.baseline_h1
                self.idle_baseline_pabs = self.baseline_pabs

            return self._make_status("INIT", win_feat)

        # 7) 이벤트 판정
        event = self._classify_event(win_feat)

        # 8) 이벤트 처리
        if event == "DEVICE_ON":
            self._handle_device_on(win_feat)
        elif event == "DEVICE_OFF":
            self._handle_device_off(win_feat)
        elif event == "IDLE":
            self._update_baseline(win_feat)

        # 9) PT/CT 센서에서 계산된 현재 특징값으로 소켓별 UI 전력값을 매 frame 갱신
        self._refresh_realtime_socket_powers(win_feat)

        return self._make_status(event, win_feat)

    # ------------------------------------------------------------------
    # 이벤트 분류 (v3 - SPARK 제거)
    # ------------------------------------------------------------------
    def _classify_event(self, win_feat):
        """
        win_feat <-> baseline_feat 비교해 이벤트 결정.

        Priority:
        1. cooldown 중 -> IDLE
        2. Irms 변화 < NOISE_FLOOR AND H1 변화 미세 -> IDLE
        3. Irms 변화 크고 H1 변화도 큼 -> DEVICE_ON/OFF
        4. Irms 변화 크고 H1 변화 작음 (e.g. resistive load) -> DEVICE_ON/OFF
        5. 그 외 -> IDLE
        """
        if self.event_cooldown > 0:
            return "IDLE"

        irms_now = win_feat["Irms_adc_mean"]
        h1_now = win_feat["H1_60_mag_mean"]

        d_irms = irms_now - self.baseline_irms
        d_h1 = h1_now - self.baseline_h1

        abs_d_irms = abs(d_irms)
        abs_d_h1 = abs(d_h1)

        # 1) 노이즈
        if abs_d_irms < IRMS_NOISE_FLOOR and abs_d_h1 < H1_DEVICE_MIN * 0.5:
            return "IDLE"

        # 2) DEVICE ON/OFF: Irms 와 H1 모두 큼
        # OFF 는 mixed transient (다른 가전 plug-in 직전 dip 등) 오탐 가능성이 큼 → 더 보수적.
        # 둘 다 2배 이상이거나, d_h1 이 5배 이상으로 매우 명확하면 OFF 허용.
        if abs_d_irms >= IRMS_DEVICE_MIN and abs_d_h1 >= H1_DEVICE_MIN:
            if d_irms > 0:
                logging.info(f"[EVENT-TRIG] cond2 ON d_irms={d_irms:.1f}, d_h1={d_h1:.1f}")
                return "DEVICE_ON"
            strong_both = (abs_d_irms >= IRMS_DEVICE_MIN * 2
                           and abs_d_h1 >= H1_DEVICE_MIN * 2)
            strong_h1   = abs_d_h1 >= H1_DEVICE_MIN * 5  # TV 처럼 d_irms 본래 작은 가전 OFF 허용
            if strong_both or strong_h1:
                logging.info(f"[EVENT-TRIG] cond2 OFF d_irms={d_irms:.1f}, d_h1={d_h1:.1f}")
                return "DEVICE_OFF"
            else:
                logging.info(f"[OFF-REJECT] cond2 d_irms={d_irms:.1f}, d_h1={d_h1:.1f} "
                             f"(임계 미달, transient 가능성)")

        # 3) Irms 만 큼 (저전력 charger 등 - H1 작아도 Irms 변화로 검출)
        # cond3 OFF 는 transient(소켓 교체 등)에 너무 쉽게 fire 됨. 현재 5 클래스 모두
        # 정상 OFF 는 cond2(또는 cond2 strong_h1) 에서 잡히므로 cond3 OFF 는 비활성화.
        if abs_d_irms >= IRMS_RESISTIVE_MIN:
            if d_irms > 0:
                logging.info(f"[EVENT-TRIG] cond3 ON d_irms={d_irms:.1f}, d_h1={d_h1:.1f}")
                return "DEVICE_ON"
            else:
                logging.info(f"[OFF-REJECT] cond3 d_irms={d_irms:.1f}, d_h1={d_h1:.1f} "
                             f"(cond3 OFF 비활성)")

        # 진단: 노이즈는 아니지만 트리거 임계 미달 - fan/charger 디버깅용
        if abs_d_irms >= IRMS_NOISE_FLOOR or abs_d_h1 >= H1_DEVICE_MIN * 0.5:
            if self.frame_count % 4 == 0:  # 4 frame마다 한 번만 (스팸 방지)
                logging.info(f"[NEAR-MISS] d_irms={d_irms:.1f}, d_h1={d_h1:.1f}, "
                             f"baseline_irms={self.baseline_irms:.1f}, baseline_h1={self.baseline_h1:.1f}")
        return "IDLE"

    # ------------------------------------------------------------------
    # 시작 시 기기 감지
    # ------------------------------------------------------------------
    def _detect_startup_device(self, win_feat):
        """
        프로그램 시작 전에 이미 켜져 있던 기기를 감지·등록.

        INIT 시 baseline이 높으면 호출됨.
        베이스라인을 일시적으로 0으로 설정해 delta=절대값으로 취급,
        _handle_device_on 을 통해 기기를 식별·소켓에 등록.
        """
        # 진짜 idle 베이스라인은 0으로 가정
        self.idle_baseline_irms = 0.0
        self.idle_baseline_h1 = 0.0

        # 베이스라인을 0으로 설정 → delta = 현재 절대값
        self.baseline_irms = 0.0
        self.baseline_h1 = 0.0
        self.baseline_pabs = 0.0
        self.baseline_feat = {k: 0.0 for k in self.feature_names}

        # _handle_device_on 이 내부적으로 _identify_device(mode='on') 호출 후 등록
        self._handle_device_on(win_feat)

    # ------------------------------------------------------------------
    # 가전 식별
    # ------------------------------------------------------------------
    def _identify_device(self, win_feat, mode="on"):
        """
        가전 식별.

        mode='on' : 켜진 기기 식별.
            1) delta 기반 RF (베이스라인 제거 → 추가된 기기만 반영)
            2) 절대값 기반 RF (단일 기기일 때 학습 분포와 일치)
            3) H1 기반 fan/charger 최종 보정 (학습 데이터 클래스 범위 근거)
            4) 범위 매칭 fallback

        mode='off' : 꺼진 기기 식별.
            "제거된 신호" (baseline - current) 를 RF 에 넣어
            active_devices 중 가장 잘 맞는 기기를 선택.

        Returns (device_name, confidence, method)
        """
        classes = list(self.model.classes_)

        # ==============================================================
        # OFF 모드: 제거된 신호로 RF 실행 → 꺼진 기기 판별
        # ==============================================================
        if mode == "off":
            if not self.active_devices:
                X = pd.DataFrame([win_feat])[self.feature_names].fillna(0.0)
                probs = self.model.predict_proba(X)[0]
                rf_pred = classes[int(np.argmax(probs))]
                return rf_pred, float(max(probs)), "rf_no_active"

            # baseline - current = 방금 꺼진 기기의 신호 근사
            if self.baseline_feat:
                removed_feat = {
                    k: max(self.baseline_feat.get(k, 0.0) - win_feat.get(k, 0.0), 0.0)
                    for k in self.feature_names
                }
                X_rem = pd.DataFrame([removed_feat])[self.feature_names].fillna(0.0)
                probs_rem = self.model.predict_proba(X_rem)[0]
                prob_dict = {c: round(float(p), 3) for c, p in zip(classes, probs_rem)}
            else:
                X = pd.DataFrame([win_feat])[self.feature_names].fillna(0.0)
                probs_arr = self.model.predict_proba(X)[0]
                prob_dict = {c: round(float(p), 3) for c, p in zip(classes, probs_arr)}

            active = list(self.active_devices.keys())
            sub = sorted(((c, prob_dict.get(c, 0.0)) for c in active),
                         key=lambda x: -x[1])
            best_dev, best_p = sub[0]
            logging.info(f"[ID-OFF] removed_probs={prob_dict}, active={active}, "
                         f"removed={best_dev}({best_p:.2f})")

            # Signature sanity: OFF 의 H1 감소량이 해당 기기의 ON 당시 H1 기여(sig)의
            # 55% 미만이면, 실제 OFF 가 아닌 baseline drift / 다른 기기 잔향으로 본다.
            # - 임계 55% 근거:
            #   case1: dryer sig H1≈38000 에서 d_h1=-444 잔향 → 444/38000=1% < 55% → 올바르게 reject
            #   case2: cleaner 꺼질 때 첫 단계 신호(d_h1=-571)가 TV OFF 로 오분류
            #          → tv sig_h1=1144, 571/1144=50% → 30% 임계로는 통과했으나 55% 로 reject ✓
            #          실제 TV OFF 는 d_h1≈1144 이상 → 1144/1144=100% → 통과 ✓
            sig = self.device_signatures.get(best_dev, {})
            sig_h1 = abs(sig.get("delta_h1", 0.0))
            d_h1_now = abs(win_feat.get("H1_60_mag_mean", 0.0) - self.baseline_h1)
            if sig_h1 > H1_DEVICE_MIN * 2 and d_h1_now < sig_h1 * 0.55:
                logging.warning(
                    f"[OFF SIG-MISMATCH] {best_dev} sig_h1={sig_h1:.0f}, "
                    f"d_h1={d_h1_now:.0f} (<30% of sig) - 부분 변동, OFF 무시"
                )
                return best_dev, 0.0, "rf_removed_signature_mismatch"

            return best_dev, best_p, "rf_removed_signal"

        # ==============================================================
        # ON 모드
        # ==============================================================

        # ① 절대값 기반 RF (단일 기기, 베이스라인≈0 상황에서 학습 분포와 일치)
        X_abs = pd.DataFrame([win_feat])[self.feature_names].fillna(0.0)
        probs_abs = self.model.predict_proba(X_abs)[0]
        rf_pred_abs = classes[int(np.argmax(probs_abs))]
        rf_conf_abs = float(max(probs_abs))
        prob_dict_abs = {c: round(float(p), 3) for c, p in zip(classes, probs_abs)}

        # ② delta 기반 RF (멀티 기기 / 베이스라인 오프셋 제거)
        rf_pred_delta = rf_pred_abs
        rf_conf_delta = rf_conf_abs
        if self.baseline_feat:
            delta_feat = {
                k: win_feat.get(k, 0.0) - self.baseline_feat.get(k, 0.0)
                for k in self.feature_names
            }
            X_delta = pd.DataFrame([delta_feat])[self.feature_names].fillna(0.0)
            probs_delta = self.model.predict_proba(X_delta)[0]
            rf_pred_delta = classes[int(np.argmax(probs_delta))]
            rf_conf_delta = float(max(probs_delta))
            prob_dict_delta = {c: round(float(p), 3) for c, p in zip(classes, probs_delta)}
        else:
            prob_dict_delta = prob_dict_abs

        # ③ 베이스라인 대비 delta 값 계산 (범위 매칭·보정에 사용)
        delta_irms = win_feat.get("Irms_adc_mean", 0.0) - self.baseline_irms
        delta_h1   = win_feat.get("H1_60_mag_mean", 0.0) - self.baseline_h1

        logging.info(
            f"[ID-ON] RF_abs={rf_pred_abs}({rf_conf_abs:.2f})  "
            f"RF_delta={rf_pred_delta}({rf_conf_delta:.2f})  "
            f"delta_irms={delta_irms:.1f}  delta_h1={delta_h1:.1f}"
        )
        logging.info(f"[ID-ON] probs_abs={prob_dict_abs}")
        logging.info(f"[ID-ON] probs_delta={prob_dict_delta}")

        # ④ 두 RF 결과 중 신뢰도가 더 높은 것을 채택
        if rf_conf_abs >= rf_conf_delta:
            rf_pred, rf_conf = rf_pred_abs, rf_conf_abs
        else:
            rf_pred, rf_conf = rf_pred_delta, rf_conf_delta

        # ⑤-a microwave 보정 (high-H1 영역)
        #   훈련: microwave Irms=[468-530], H1=[19938-24309]
        #   dryer 의 넓은 Irms 범위(67-763)가 이 구간을 포함 → RF 오분류 방지
        #   단 dryer 강풍(Irms~700, H1~31000)이 잘못 microwave 로 보정되지 않도록
        #   Irms 상한(560)도 함께 검사.
        if delta_h1 > 19000:
            if 455 < delta_irms < 560 and delta_h1 < 26000:
                high_h1_label = "microwave"
            else:
                high_h1_label = None  # dryer 영역 (Irms>560 또는 H1>26000) → RF 에 위임

            if high_h1_label and rf_pred != high_h1_label:
                logging.info(
                    f"[ID-ON] high-H1 override: {rf_pred} -> {high_h1_label}  "
                    f"(delta_irms={delta_irms:.1f}, delta_h1={delta_h1:.1f})"
                )
                rf_pred = high_h1_label

        # ⑤-b charger vs tv 보정
        #   훈련(charger 재수집): charger Irms 104-107, H1 364-499 / tv Irms 79-83, H1 1240-1594
        #   Irms 가 거의 겹쳐 RF 가 혼동하기 쉬움 → H1 boundary 로 강제 분리
        #   단 partial ramp 라서 boundary 결과가 이미 active 한 가전이면 alternate 채택
        #   (안 그러면 두 번째 가전이 SKIP 되어 영영 등록 안 됨)
        if rf_pred in ("charger", "tv") and delta_h1 > H1_DEVICE_MIN:
            h1_label = "charger" if delta_h1 < CHARGER_TV_H1_BOUNDARY else "tv"
            if h1_label in self.active_devices:
                alternate = "tv" if h1_label == "charger" else "charger"
                if alternate not in self.active_devices:
                    logging.info(
                        f"[ID-ON] H1 override alternate: {h1_label} 이미 active → {alternate}"
                    )
                    h1_label = alternate
            if h1_label != rf_pred:
                logging.info(
                    f"[ID-ON] H1 override: {rf_pred} -> {h1_label}  "
                    f"(delta_h1={delta_h1:.1f}, boundary={CHARGER_TV_H1_BOUNDARY})"
                )
                rf_pred = h1_label

        if rf_conf >= RF_CONFIDENCE_THRESHOLD:
            return rf_pred, rf_conf, "rf+h1_correction"

        # ⑥ 저신뢰도 fallback: Irms + H1 범위 매칭
        range_pred = self._range_match(delta_irms, delta_h1)
        logging.info(f"[ID-ON] low-conf fallback: range_match={range_pred}")
        return (range_pred or rf_pred), 0.5, "range_fallback"

    def _range_match(self, delta_irms, delta_h1):
        """
        delta_irms / delta_h1 이 가장 잘 맞는 기기 클래스를 반환.
        범위 밖으로 벗어난 거리(penalty)가 가장 작은 기기를 선택.
        """
        best_dev = None
        best_score = float("inf")
        for dev, r in self.class_ranges.items():
            irms_lo = r.get("Irms_adc_p10", 0.0)
            irms_hi = r.get("Irms_adc_p90", float("inf"))
            h1_lo   = r.get("H1_60_mag_p10", 0.0)
            h1_hi   = r.get("H1_60_mag_p90", float("inf"))
            irms_pen = max(0.0, irms_lo - delta_irms, delta_irms - irms_hi)
            h1_pen   = max(0.0, h1_lo   - delta_h1,   delta_h1   - h1_hi)
            score = irms_pen + h1_pen
            if score < best_score:
                best_score = score
                best_dev = dev
        return best_dev

    # ------------------------------------------------------------------
    # ON / OFF 핸들러
    # ------------------------------------------------------------------
    def _handle_device_on(self, win_feat):
        # 이벤트 직전 베이스라인 저장 (재분류 시 delta 계산용)
        self.pre_event_baseline_irms = self.baseline_irms
        self.pre_event_baseline_h1 = self.baseline_h1
        self.pre_event_baseline_feat = dict(self.baseline_feat) if self.baseline_feat else None

        # delta 계산 (식별 전에 먼저 구해야 signature 저장에 사용 가능)
        delta_irms = win_feat.get("Irms_adc_mean", 0.0) - self.baseline_irms
        delta_h1   = win_feat.get("H1_60_mag_mean", 0.0) - self.baseline_h1
        delta_pabs = win_feat.get("Pabs_mean_proxy_mean", 0.0) - self.baseline_feat.get("Pabs_mean_proxy_mean", 0.0)

        dev_name, conf, method = self._identify_device(win_feat, mode="on")

        # 이미 켜진 가전 -> 무시
        if dev_name in self.active_devices:
            logging.info(f"[ON SKIP] {dev_name} already active")
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        # DEVICE_OFF 상태 같은 가전 소켓 우선 재사용
        target_sk = None
        for sk in self.sockets:
            if sk.state == "DEVICE_OFF" and sk.device == dev_name:
                target_sk = sk
                break

        # 없으면 EMPTY 소켓
        if target_sk is None:
            for sk in self.sockets:
                if sk.state == "EMPTY":
                    target_sk = sk
                    break

        # 그래도 없으면 DEVICE_OFF 소켓 재활용 (소켓 4개 < 사용 기기 5+ 인 경우)
        # 가장 낮은 인덱스의 DEVICE_OFF 소켓 회수 — 실제로 콘센트에서 뽑힌 자리로 간주
        if target_sk is None:
            for sk in self.sockets:
                if sk.state == "DEVICE_OFF":
                    logging.info(
                        f"[SOCKET RECYCLE] Socket{sk.idx} ({sk.device}) → {dev_name} (재활용)"
                    )
                    target_sk = sk
                    break

        if target_sk is None:
            logging.warning(f"[ON FAIL] {dev_name} - no available socket")
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        power_w = self._estimate_new_device_power_w()
        mode = ""
        target_sk.assign_device(dev_name, power_w, mode)
        self.active_devices[dev_name] = target_sk.idx

        # 기기 기여값 기록 (멀티 기기 OFF 감지에 사용)
        self.device_signatures[dev_name] = {
            "delta_irms": delta_irms,
            "delta_h1":   delta_h1,
            "delta_pabs": delta_pabs,
        }

        logging.info(f"[DEVICE ON] Socket{target_sk.idx} <- {dev_name} "
                     f"({power_w:.0f}W, conf={conf:.2f}, method={method}, "
                     f"d_irms={delta_irms:.1f}, d_h1={delta_h1:.1f}, d_pabs={delta_pabs:.1f})")

        self.event_cooldown = EVENT_COOLDOWN_FRAMES
        self.baseline_feat = dict(win_feat)
        self.baseline_irms = win_feat["Irms_adc_mean"]
        self.baseline_h1 = win_feat["H1_60_mag_mean"]
        self.baseline_pabs = win_feat.get("Pabs_mean_proxy_mean", self.baseline_pabs)
        self.event_history.append((self.frame_count, "ON", dev_name))

        # 혼합 창 문제 보정: steady-state 안정 후 재분류
        self.reclassify_countdown = RECLASSIFY_DELAY

    def _handle_device_off(self, win_feat):
        if not self.active_devices:
            d_irms = win_feat.get("Irms_adc_mean", 0.0) - self.baseline_irms
            d_h1   = win_feat.get("H1_60_mag_mean", 0.0) - self.baseline_h1
            logging.warning(
                f"[OFF SKIP] no active devices  d_irms={d_irms:.1f}, d_h1={d_h1:.1f}, "
                f"Irms_now={win_feat.get('Irms_adc_mean', 0.0):.1f}, "
                f"H1_now={win_feat.get('H1_60_mag_mean', 0.0):.1f}, "
                f"baseline_irms={self.baseline_irms:.1f}, baseline_h1={self.baseline_h1:.1f}"
            )
            # active 가전 0인 상태에서 baseline drift 로 인한 반복 OFF SKIP 차단:
            # 직후 baseline 을 win_feat 으로 즉시 동기화하여 d 를 0 으로 리셋
            self.baseline_feat = dict(win_feat)
            self.baseline_irms = win_feat.get("Irms_adc_mean", self.baseline_irms)
            self.baseline_h1   = win_feat.get("H1_60_mag_mean", self.baseline_h1)
            self.baseline_pabs = win_feat.get("Pabs_mean_proxy_mean", self.baseline_pabs)
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        dev_name, conf, method = self._identify_device(win_feat, mode="off")

        # OFF 가드: RF 가 해당 가전을 사실상 OFF로 인지 못 한 경우(conf 매우 낮음)
        # 거짓 transient 가능성이 높음 → 무시. active 가전 1개뿐이라 강제로 picked 된 케이스 차단.
        OFF_CONF_MIN = 0.05
        if conf < OFF_CONF_MIN:
            logging.warning(
                f"[OFF REJECT] {dev_name} conf={conf:.2f} < {OFF_CONF_MIN} - transient 가능성"
            )
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        sk_idx = self.active_devices.get(dev_name)
        if sk_idx is None:
            logging.warning(f"[OFF FAIL] {dev_name} not in active list")
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        target_sk = next((s for s in self.sockets if s.idx == sk_idx), None)
        if target_sk is None:
            logging.warning(f"[OFF FAIL] socket{sk_idx} not found")
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            return

        target_sk.turn_off()
        del self.active_devices[dev_name]
        self.device_signatures.pop(dev_name, None)
        self.reclassify_countdown = 0  # 이전 ON 이벤트의 재분류 취소

        logging.info(f"[DEVICE OFF] Socket{target_sk.idx} ({dev_name}) "
                     f"(conf={conf:.2f}, method={method})")

        self.event_cooldown = EVENT_COOLDOWN_FRAMES
        self.baseline_feat = dict(win_feat)
        self.baseline_irms = win_feat["Irms_adc_mean"]
        self.baseline_h1 = win_feat["H1_60_mag_mean"]
        self.baseline_pabs = win_feat.get("Pabs_mean_proxy_mean", self.baseline_pabs)
        self.event_history.append((self.frame_count, "OFF", dev_name))

        # 모든 기기가 꺼지면 idle baseline 갱신
        if not self.active_devices:
            self.idle_baseline_irms = self.baseline_irms
            self.idle_baseline_h1 = self.baseline_h1
            self.idle_baseline_pabs = self.baseline_pabs
            self.idle_baseline_pabs = self.baseline_pabs

    def _update_baseline(self, win_feat):
        """IDLE 시 baseline EMA 갱신 + 멀티 기기 OFF 감지 + 재분류.

        변화 중(d 가 노이즈 위)에는 EMA 를 거의 freeze 한다.
        그렇지 않으면 ramp 가 느린 기기(fan H1: 5초+) 의 delta 가 baseline 추격에 묻혀
        이벤트 임계를 못 넘는다.
        """
        d_irms = win_feat.get("Irms_adc_mean", 0.0) - self.baseline_irms
        d_h1   = win_feat.get("H1_60_mag_mean", 0.0) - self.baseline_h1
        is_stable = (abs(d_irms) < IRMS_NOISE_FLOOR
                     and abs(d_h1) < H1_DEVICE_MIN * 0.5)
        a = EMA_ALPHA if is_stable else EMA_ALPHA * 0.05

        for k, v in win_feat.items():
            if k in self.baseline_feat:
                self.baseline_feat[k] = (1 - a) * self.baseline_feat[k] + a * v
        self.baseline_irms = self.baseline_feat["Irms_adc_mean"]
        self.baseline_h1 = self.baseline_feat["H1_60_mag_mean"]
        self.baseline_pabs = self.baseline_feat.get("Pabs_mean_proxy_mean", self.baseline_pabs)

        # 모든 기기가 꺼진 상태면 idle baseline 업데이트
        if not self.active_devices:
            self.idle_baseline_irms = self.baseline_irms
            self.idle_baseline_h1 = self.baseline_h1
            self.idle_baseline_pabs = self.baseline_pabs

        # 기기가 2개 이상 켜진 경우: 개별 기기 꺼짐 감지
        if len(self.active_devices) >= 2:
            self._sanity_check_active_devices(win_feat)

        # 재분류 카운트다운 (기동 과도전류 이후 steady-state 창으로 재확인)
        if self.reclassify_countdown > 0 and self.active_devices:
            self.reclassify_countdown -= 1
            if self.reclassify_countdown == 0:
                self._reclassify_latest_device(win_feat)

    def _sanity_check_active_devices(self, win_feat):
        """
        멀티 기기 상황에서 꺼진 기기를 탐지.

        원리: H1(60Hz 고조파)은 근사적으로 선형 합산 가능.
            expected_H1_all = idle_H1 + sum(각 기기 H1 기여)
            기기 X가 꺼지면: H1_now ≈ expected_H1_all - X의 H1 기여

        이벤트 트리거 없이 주기적으로 실행되므로
        큰 기기에 묻혀 이벤트가 발생하지 않은 소형 기기의 꺼짐도 감지 가능.
        """
        if self.event_cooldown > 0 or not self.device_signatures:
            return

        h1_now = win_feat.get("H1_60_mag_mean", 0.0)

        total_delta_h1 = sum(
            sig.get("delta_h1", 0.0) for sig in self.device_signatures.values()
        )
        expected_h1_all = self.idle_baseline_h1 + total_delta_h1

        for dev_name in list(self.active_devices.keys()):
            sig = self.device_signatures.get(dev_name)
            if sig is None:
                continue
            dev_delta_h1 = sig.get("delta_h1", 0.0)
            # H1 기여가 작은 기기(예: H/W charger 가 ~150 만 기여)는 H1 측정 노이즈(±50)에
            # 묻혀 sanity 판단 자체가 불안정. 충분히 큰 기여(>=500)만 검사 대상.
            if abs(dev_delta_h1) < SANITY_CHECK_H1_MIN:
                continue

            expected_h1_without = expected_h1_all - dev_delta_h1
            diff_with    = abs(h1_now - expected_h1_all)
            diff_without = abs(h1_now - expected_h1_without)

            # 현재 H1이 "이 기기 없을 때" 예상값에 훨씬 가까우면 → 꺼진 것
            if diff_without < diff_with * 0.4 and diff_with > H1_DEVICE_MIN * 2:
                logging.info(
                    f"[SANITY-OFF] '{dev_name}' H1 기여 소멸 감지 "
                    f"(h1_now={h1_now:.0f}, expected_all={expected_h1_all:.0f}, "
                    f"expected_without={expected_h1_without:.0f})"
                )
                self._force_device_off(dev_name)
                break  # 한 프레임에 하나씩 처리

    def _reclassify_latest_device(self, win_feat):
        """
        이벤트 발생 직후는 혼합 창(일부 empty + 일부 device 프레임)이라
        RF 분류가 틀릴 수 있다.
        RECLASSIFY_DELAY IDLE 프레임 후 steady-state 창으로 재확인.

        - 기기 1개: 절대값 RF (단일 기기 학습 분포와 일치)
        - 기기 2개+: pre_event_baseline 대비 delta RF (추가 기기의 순수 신호)
        """
        if not self.active_devices:
            return

        classes = list(self.model.classes_)

        if len(self.active_devices) == 1:
            # 단일 기기: steady-state 절대값 RF
            dev_name = next(iter(self.active_devices))
            X = pd.DataFrame([win_feat])[self.feature_names].fillna(0.0)
            probs = self.model.predict_proba(X)[0]
            rf_pred = classes[int(np.argmax(probs))]
            rf_conf = float(max(probs))
            prob_dict = {c: round(float(p), 3) for c, p in zip(classes, probs)}
            logging.info(
                f"[RECLASSIFY-1] 기존='{dev_name}'  RF(abs)={rf_pred}({rf_conf:.2f})  "
                f"Irms={win_feat.get('Irms_adc_mean',0):.1f}  "
                f"H1={win_feat.get('H1_60_mag_mean',0):.1f}  "
                f"probs={prob_dict}"
            )
        else:
            # 멀티 기기: pre-event 베이스라인 대비 delta RF
            if not self.pre_event_baseline_feat:
                return
            # 가장 최근 ON 기기를 대상으로 함
            dev_name = list(self.active_devices.keys())[-1]
            delta_feat = {
                k: win_feat.get(k, 0.0) - self.pre_event_baseline_feat.get(k, 0.0)
                for k in self.feature_names
            }
            X = pd.DataFrame([delta_feat])[self.feature_names].fillna(0.0)
            probs = self.model.predict_proba(X)[0]
            rf_pred = classes[int(np.argmax(probs))]
            rf_conf = float(max(probs))
            prob_dict = {c: round(float(p), 3) for c, p in zip(classes, probs)}
            logging.info(
                f"[RECLASSIFY-N] 기존='{dev_name}'  RF(delta)={rf_pred}({rf_conf:.2f})  "
                f"d_Irms={win_feat.get('Irms_adc_mean',0)-self.pre_event_baseline_irms:.1f}  "
                f"d_H1={win_feat.get('H1_60_mag_mean',0)-self.pre_event_baseline_h1:.1f}  "
                f"probs={prob_dict}"
            )

        # H1 기반 charger/tv 보정 적용 (active 인 가전이면 alternate)
        d_h1_from_pre = win_feat.get("H1_60_mag_mean", 0.0) - self.pre_event_baseline_h1
        if rf_pred in ("charger", "tv") and abs(d_h1_from_pre) > H1_DEVICE_MIN:
            h1_label = "charger" if d_h1_from_pre < CHARGER_TV_H1_BOUNDARY else "tv"
            if h1_label in self.active_devices and h1_label != dev_name:
                alternate = "tv" if h1_label == "charger" else "charger"
                if alternate not in self.active_devices:
                    h1_label = alternate
            if h1_label != rf_pred:
                logging.info(f"[RECLASSIFY] H1 보정: {rf_pred} -> {h1_label}")
                rf_pred = h1_label

        RECLASSIFY_CONF = 0.45  # 부분 ramp 상태에서 잘못 등록된 cooker→dryer 등 보정용. dryer 0.49 같은 경계 케이스도 통과시킴.
        if rf_pred == dev_name:
            logging.info(f"[RECLASSIFY] '{dev_name}' 재확인 완료 (conf={rf_conf:.2f})")
            return

        if rf_conf < RECLASSIFY_CONF:
            logging.info(
                f"[RECLASSIFY] 신뢰도 부족 ({rf_pred} {rf_conf:.2f} < {RECLASSIFY_CONF}). "
                f"'{dev_name}' 유지."
            )
            return

        if rf_pred in self.active_devices:
            logging.info(f"[RECLASSIFY] '{rf_pred}' 이미 active. 재분류 취소.")
            return

        # 재분류 실행
        logging.info(f"[RECLASSIFY] '{dev_name}' -> '{rf_pred}' (conf={rf_conf:.2f})")
        sk_idx = self.active_devices.pop(dev_name, None)
        if sk_idx is None:
            return
        old_sig = self.device_signatures.pop(dev_name, {})

        target_sk = next((s for s in self.sockets if s.idx == sk_idx), None)
        if target_sk:
            # 재분류는 같은 소켓의 기기명만 바뀌는 것이므로 현재 소켓 전력은 그대로 유지
            target_sk.assign_device(rf_pred, target_sk.power_w, "")
            self.active_devices[rf_pred] = sk_idx
            # 재분류 시점의 steady-state win_feat 으로 signature 갱신.
            # 그대로 old_sig 를 쓰면 cleaner→dryer 같은 reclass 후 dryer 의 sig 가
            # 여전히 cleaner ramp 시점의 작은 값(예: ΔH1=3876)이라 OFF sanity check 가 무너진다.
            self.device_signatures[rf_pred] = {
                "delta_irms": win_feat.get("Irms_adc_mean", 0.0) - self.pre_event_baseline_irms,
                "delta_h1":   win_feat.get("H1_60_mag_mean", 0.0) - self.pre_event_baseline_h1,
                "delta_pabs": win_feat.get("Pabs_mean_proxy_mean", 0.0) - self.pre_event_baseline_feat.get("Pabs_mean_proxy_mean", 0.0),
            }
            self.event_history.append((self.frame_count, "RECLASSIFY", f"{dev_name}->{rf_pred}"))
            # 재분류 후 쿨다운 리셋 + 베이스라인 갱신
            # 기동 과도전류(inrush) 이후 미세 이벤트 억제
            self.event_cooldown = EVENT_COOLDOWN_FRAMES
            self.baseline_feat  = dict(win_feat)
            self.baseline_irms  = win_feat.get("Irms_adc_mean", self.baseline_irms)
            self.baseline_h1    = win_feat.get("H1_60_mag_mean", self.baseline_h1)
            self.baseline_pabs  = win_feat.get("Pabs_mean_proxy_mean", self.baseline_pabs)

    def _force_device_off(self, dev_name):
        """Sanity check 결과로 특정 기기를 강제 OFF 처리."""
        sk_idx = self.active_devices.get(dev_name)
        if sk_idx is None:
            return
        target_sk = next((s for s in self.sockets if s.idx == sk_idx), None)
        if target_sk is None:
            return

        target_sk.turn_off()
        del self.active_devices[dev_name]
        self.device_signatures.pop(dev_name, None)
        self.event_cooldown = EVENT_COOLDOWN_FRAMES
        self.event_history.append((self.frame_count, "OFF", dev_name))

        logging.info(
            f"[FORCE OFF] Socket{target_sk.idx} ({dev_name}) "
            f"by H1 sanity check"
        )

        if not self.active_devices:
            self.idle_baseline_irms = self.baseline_irms
            self.idle_baseline_h1 = self.baseline_h1

    # ------------------------------------------------------------------
    # PT/CT 센서 raw 기반 실시간 전력 계산
    # ------------------------------------------------------------------
    def _rms_np(self, x):
        x = np.asarray(x, dtype=np.float64)
        if len(x) == 0:
            return 0.0
        return float(np.sqrt(np.mean(x ** 2)))

    def _clean_power_signal(self, x):
        """전력 계산용 raw 파형 전처리: 스파이크 clip + DC 제거."""
        x = np.asarray(x, dtype=np.float64)
        if len(x) < 10:
            return x
        lo = np.percentile(x, 1)
        hi = np.percentile(x, 99)
        if lo < hi:
            x = np.clip(x, lo, hi)
        return x - np.mean(x)

    def _compute_ptct_power_metrics(self, ch0, ch1):
        """
        CH0(PT 전압파형), CH1(CT/ACS 전류파형) raw ADC에서 실시간 전력 계산.

        여기서는 기기명별 고정 W를 전혀 쓰지 않는다.
        계산식:
            v_adc = ch0_centered * ADC_VREF / ADC_FULL_SCALE
            i_adc = ch1_centered * ADC_VREF / ADC_FULL_SCALE
            v(t)  = PT 파형을 220Vrms로 정규화한 전압파형
            i(t)  = i_adc / CURRENT_SENSOR_SENSITIVITY_V_PER_A
            P     = mean(v(t) * i(t))
        """
        ch0 = self._clean_power_signal(ch0)
        ch1 = self._clean_power_signal(ch1)
        n = min(len(ch0), len(ch1))
        if n < 10:
            return {
                "real_power_w": 0.0,
                "apparent_power_va": 0.0,
                "display_power_w": 0.0,
                "vrms_v": 0.0,
                "irms_a": 0.0,
                "pf": 0.0,
            }

        ch0 = ch0[:n]
        ch1 = ch1[:n]
        adc_to_v = ADC_VREF / ADC_FULL_SCALE

        v_adc = ch0 * adc_to_v
        i_adc = ch1 * adc_to_v

        v_adc_rms = self._rms_np(v_adc)
        if v_adc_rms <= 1e-9:
            v_actual = np.zeros_like(v_adc)
        elif USE_NOMINAL_VOLTAGE_RMS:
            # PT 보정상수 없이도 전압 파형의 위상/모양은 쓰고, RMS만 220V로 맞춘다.
            v_actual = (v_adc / v_adc_rms) * MAINS_VRMS_NOMINAL
        else:
            v_actual = v_adc * VOLTAGE_SENSOR_SCALE_V_PER_ADC_V

        # CT/ACS 전류 환산. 센서 종류가 다르면 CURRENT_SENSOR_SENSITIVITY_V_PER_A만 조정.
        if CURRENT_SENSOR_SENSITIVITY_V_PER_A <= 0:
            i_actual = np.zeros_like(i_adc)
        else:
            i_actual = i_adc / CURRENT_SENSOR_SENSITIVITY_V_PER_A

        vrms_v = self._rms_np(v_actual)
        irms_a = self._rms_np(i_actual)
        p_inst = v_actual * i_actual
        real_power_w = float(np.mean(p_inst)) if len(p_inst) else 0.0

        if INVERT_POWER_POLARITY:
            real_power_w = -real_power_w
        if USE_ABS_ACTIVE_POWER:
            real_power_w = abs(real_power_w)

        apparent_power_va = float(vrms_v * irms_a)
        pf = float(real_power_w / apparent_power_va) if apparent_power_va > 1e-9 else 0.0

        if POWER_DISPLAY_MODE == "apparent":
            display_power_w = apparent_power_va
        else:
            display_power_w = real_power_w

        if display_power_w < POWER_DISPLAY_DEADBAND_W:
            display_power_w = 0.0

        return {
            "real_power_w": float(real_power_w),
            "apparent_power_va": float(apparent_power_va),
            "display_power_w": float(display_power_w),
            "vrms_v": float(vrms_v),
            "irms_a": float(irms_a),
            "pf": float(pf),
        }

    def _update_realtime_power_metrics(self, ch0, ch1):
        """매 frame마다 PT/CT raw 기반 전체 전력값을 갱신한다."""
        m = self._compute_ptct_power_metrics(ch0, ch1)
        self.latest_total_power_w = m["display_power_w"]
        self.latest_apparent_power_va = m["apparent_power_va"]
        self.latest_vrms_v = m["vrms_v"]
        self.latest_irms_a = m["irms_a"]
        self.latest_power_factor = m["pf"]

    def _estimate_new_device_power_w(self):
        """
        새 기기가 ON 된 순간의 소켓 전력.
        단일 기기면 전체 PT/CT 전력 그대로, 이미 켜진 기기가 있으면 증가분을 사용한다.
        """
        total = max(float(self.latest_total_power_w), 0.0)
        active_sum = sum(
            max(float(s.power_w), 0.0)
            for s in self.sockets
            if s.state == "DEVICE_ON"
        )
        if active_sum <= 0:
            return total
        return max(total - active_sum, 0.0)

    def _refresh_realtime_socket_powers(self, win_feat):
        """
        Matplotlib UI와 mobile_ui가 볼 SocketFSM.power_w를 PT/CT raw 기반 전력으로 갱신한다.

        중요:
        - active 기기가 1개면 그 소켓 전력 = 현재 전체 PT/CT 전력이다.
        - active 기기가 여러 개면 단일 PT/CT 센서로는 소켓별 실제 전력을 직접 분리 측정할 수 없어서,
          현재 전체 전력을 기존 소켓 전력 비율로 나눈다. 전체 전력 합은 항상 PT/CT raw 계산값과 맞춘다.
        """
        total_power = max(float(self.latest_total_power_w), 0.0)

        with self.status_lock:
            active_sockets = [s for s in self.sockets if s.state == "DEVICE_ON"]
            if not active_sockets:
                return

            if len(active_sockets) == 1:
                sk = active_sockets[0]
                new_power = total_power
                if sk.power_w > 0:
                    sk.power_w = (1.0 - POWER_SMOOTH_ALPHA) * sk.power_w + POWER_SMOOTH_ALPHA * new_power
                else:
                    sk.power_w = new_power
                sk.mode = ""
                return

            prev_sum = sum(max(float(s.power_w), 0.0) for s in active_sockets)
            if prev_sum <= 1e-9:
                share = total_power / len(active_sockets)
                for sk in active_sockets:
                    sk.power_w = share
                    sk.mode = ""
                return

            for sk in active_sockets:
                ratio = max(float(sk.power_w), 0.0) / prev_sum
                new_power = total_power * ratio
                sk.power_w = (1.0 - POWER_SMOOTH_ALPHA) * sk.power_w + POWER_SMOOTH_ALPHA * new_power
                sk.mode = ""

    def get_mobile_status(self):
        """
        mobile_ui.py의 /api/status에서 호출된다.
        Matplotlib UI가 보고 있는 SocketFSM 값을 그대로 복사해서 모바일 UI로 넘긴다.
        """
        with self.status_lock:
            sockets = [s.to_dict() for s in self.sockets]
            total_power = float(self.latest_total_power_w)
            apparent_power = float(self.latest_apparent_power_va)
            vrms_v = float(self.latest_vrms_v)
            irms_a = float(self.latest_irms_a)
            pf = float(self.latest_power_factor)

        return {
            "power": {
                s["idx"]: float(s["power_w"]) if s["state"] == "DEVICE_ON" else 0.0
                for s in sockets
            },
            "device": {
                s["idx"]: (s["device"] or "")
                for s in sockets
            },
            "mode": {
                s["idx"]: (s.get("mode") or "")
                for s in sockets
            },
            "socket_state": {
                s["idx"]: s["state"]
                for s in sockets
            },
            "total_power_w": total_power,
            "apparent_power_va": apparent_power,
            "vrms_v": vrms_v,
            "irms_a": irms_a,
            "power_factor": pf,
        }


    # ------------------------------------------------------------------
    # 상태 dict
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
            "fs_actual": self._last_fs,
            "ch0": self._last_ch0,
            "ch1": self._last_ch1,
            "total_power_w": self.latest_total_power_w,
            "apparent_power_va": self.latest_apparent_power_va,
            "vrms_v": self.latest_vrms_v,
            "irms_a": self.latest_irms_a,
            "power_factor": self.latest_power_factor,
        }


# =====================================================================
# 3. AIDashboardUI - 4 소켓 + 오실로스코프 + 디버그
# =====================================================================

class AIDashboardUI:
    """
    NILM 시연 UI.

    Layout (3 row):
      Row 1: 4 소켓 박스 (state, device, power)
      Row 2: 오실로스코프 (CH0 voltage, CH1 current)
      Row 3: 디버그 정보 (event, baseline, current win_feat, active list)
    """

    # 상태별 색상
    COLOR_EMPTY = "#404040"      # gray
    COLOR_ON = "#00C853"          # green
    COLOR_OFF = "#FF8C00"         # orange
    COLOR_BORDER_EMPTY = "#888888"
    COLOR_BORDER_ON = "#00FF00"
    COLOR_BORDER_OFF = "#FFA500"

    def __init__(self, dsp_engine):
        self.engine = dsp_engine
        self.buffer_size = self.engine.buffer_size

        # ---- figure ----
        self.fig = plt.figure(figsize=(13, 9))
        self.fig.canvas.manager.set_window_title('WattsUp NILM Monitor v3')
        self.fig.patch.set_facecolor('#1e1e1e')

        gs = self.fig.add_gridspec(
            3, N_SOCKETS,
            height_ratios=[1.0, 1.3, 0.9],
            hspace=0.45, wspace=0.25,
            left=0.05, right=0.97, top=0.94, bottom=0.05,
        )

        # ---- Row 1: 소켓 4개 ----
        self.socket_axes = []
        self.socket_rects = []
        self.socket_state_labels = []
        self.socket_device_labels = []
        self.socket_power_labels = []

        for i in range(N_SOCKETS):
            ax = self.fig.add_subplot(gs[0, i])
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)
            ax.set_xticks([]); ax.set_yticks([])
            ax.set_facecolor('#1e1e1e')
            for spine in ax.spines.values():
                spine.set_edgecolor('gray')
            ax.set_title(f"Socket {i+1}", color='white', fontsize=13,
                         fontweight='bold', pad=8)

            # 배경 박스 (큰 사각형)
            rect = plt.Rectangle(
                (0.05, 0.05), 0.9, 0.9,
                facecolor=self.COLOR_EMPTY,
                edgecolor=self.COLOR_BORDER_EMPTY,
                linewidth=3,
            )
            ax.add_patch(rect)
            self.socket_rects.append(rect)

            # device name (소켓 중상단)
            dev_txt = ax.text(
                0.5, 0.72, "",
                ha='center', va='center', color='white',
                fontsize=18, fontweight='bold',
                transform=ax.transAxes,
            )
            self.socket_device_labels.append(dev_txt)

            # state (소켓 중앙)
            state_txt = ax.text(
                0.5, 0.5, "EMPTY",
                ha='center', va='center', color='white',
                fontsize=20, fontweight='bold',
                transform=ax.transAxes,
            )
            self.socket_state_labels.append(state_txt)

            # power (소켓 하단)
            pwr_txt = ax.text(
                0.5, 0.22, "",
                ha='center', va='center', color='#FFFF00',
                fontsize=16, fontweight='bold',
                transform=ax.transAxes,
            )
            self.socket_power_labels.append(pwr_txt)

            self.socket_axes.append(ax)

        # ---- Row 2: 오실로스코프 ----
        self.ax_scope = self.fig.add_subplot(gs[1, :])
        self.line_ch0, = self.ax_scope.plot(
            np.zeros(self.buffer_size),
            color='magenta', linewidth=1.2, label='Voltage (CH0 - PT)'
        )
        self.line_ch1, = self.ax_scope.plot(
            np.zeros(self.buffer_size),
            color='cyan', linewidth=1.6, label='Current (CH1 - CT)'
        )
        self.ax_scope.set_ylim(-2048, 2048)
        self.ax_scope.set_xlim(0, self.buffer_size)
        self.ax_scope.set_facecolor('black')
        self.ax_scope.set_title("Real-time Oscilloscope",
                                color='white', fontsize=11, pad=6)
        self.ax_scope.legend(loc='upper right', fontsize=10, facecolor='#222')
        self.ax_scope.grid(True, linestyle=':', alpha=0.3, color='gray')
        self.ax_scope.tick_params(colors='white', labelsize=9)
        for spine in self.ax_scope.spines.values():
            spine.set_edgecolor('gray')

        # ---- Row 3: 디버그 ----
        self.ax_info = self.fig.add_subplot(gs[2, :])
        self.ax_info.set_facecolor('black')
        self.ax_info.set_xticks([]); self.ax_info.set_yticks([])
        for spine in self.ax_info.spines.values():
            spine.set_edgecolor('gray')

        self.info_text = self.ax_info.text(
            0.01, 0.95, "",
            transform=self.ax_info.transAxes,
            color='white', fontsize=10, family='monospace',
            verticalalignment='top',
        )

    # ------------------------------------------------------------------
    def _update_socket_ui(self, sk_dict, idx):
        st = sk_dict["state"]
        dev = sk_dict["device"]
        pwr = sk_dict["power_w"]
        mode = sk_dict.get("mode", "")

        rect = self.socket_rects[idx]
        dev_lbl = self.socket_device_labels[idx]
        state_lbl = self.socket_state_labels[idx]
        pwr_lbl = self.socket_power_labels[idx]

        if st == "EMPTY":
            rect.set_facecolor(self.COLOR_EMPTY)
            rect.set_edgecolor(self.COLOR_BORDER_EMPTY)
            dev_lbl.set_text("")
            state_lbl.set_text("EMPTY")
            state_lbl.set_color("white")
            pwr_lbl.set_text("")

        elif st == "DEVICE_ON":
            rect.set_facecolor(self.COLOR_ON)
            rect.set_edgecolor(self.COLOR_BORDER_ON)
            title = dev.upper() if dev else ""
            if mode:
                title = f"{title}\n{mode}"
            dev_lbl.set_text(title)
            state_lbl.set_text("ON")
            state_lbl.set_color("white")
            pwr_lbl.set_text(f"{pwr:.0f} W")

        elif st == "DEVICE_OFF":
            rect.set_facecolor(self.COLOR_OFF)
            rect.set_edgecolor(self.COLOR_BORDER_OFF)
            dev_lbl.set_text(dev.upper() if dev else "")
            state_lbl.set_text("OFF")
            state_lbl.set_color("white")
            pwr_lbl.set_text("0 W")

    # ------------------------------------------------------------------
    def update_frame(self, frame):
        try:
            status = self.engine.process_ai_frame()
        except Exception as e:
            logging.exception(f"process_ai_frame error: {e}")
            return []

        # 소켓
        for i, sk_dict in enumerate(status["sockets"]):
            self._update_socket_ui(sk_dict, i)

        # 오실로스코프
        ch0 = status.get("ch0")
        ch1 = status.get("ch1")
        if ch0 is not None and len(ch0) == self.buffer_size:
            self.line_ch0.set_ydata(ch0)
            self.line_ch1.set_ydata(ch1)

        # 디버그
        wf = status.get("win_feat") or {}
        info_lines = [
            "frame: {:>5d}   event: {:<12s}   cooldown: {:>2d}   fs: {:>6.1f} Hz".format(
                status["frame_count"],
                str(status["event"]),
                status["event_cooldown"],
                status["fs_actual"],
            ),
            "",
            "baseline  Irms: {:>8.2f}   H1: {:>10.2f}".format(
                status["baseline_irms"], status["baseline_h1"],
            ),
            "current   Irms: {:>8.2f}   H1: {:>10.2f}   H3: {:>8.2f}   THD: {:.3f}".format(
                wf.get("Irms_adc_mean", 0),
                wf.get("H1_60_mag_mean", 0),
                wf.get("H3_180_mag_mean", 0),
                wf.get("THD_i_mean", 0),
            ),
            "delta     Irms: {:>+8.2f}   H1: {:>+10.2f}".format(
                wf.get("Irms_adc_mean", 0) - status["baseline_irms"],
                wf.get("H1_60_mag_mean", 0) - status["baseline_h1"],
            ),
            "power    P: {:>8.1f} W   S: {:>8.1f} VA   Vrms: {:>6.1f} V   Irms: {:>5.2f} A   PF: {:.2f}".format(
                status.get("total_power_w", 0),
                status.get("apparent_power_va", 0),
                status.get("vrms_v", 0),
                status.get("irms_a", 0),
                status.get("power_factor", 0),
            ),
            "",
            "active devices: {}".format(status["active_devices"] or "{}"),
        ]
        self.info_text.set_text("\n".join(info_lines))

        out = [self.line_ch0, self.line_ch1]
        out += self.socket_rects + self.socket_state_labels
        out += self.socket_device_labels + self.socket_power_labels
        out += [self.info_text]
        return out

    # ------------------------------------------------------------------
    def start(self):
        self.ani = animation.FuncAnimation(
            self.fig, self.update_frame,
            interval=100,
            blit=False,
            cache_frame_data=False,
        )
        plt.show()