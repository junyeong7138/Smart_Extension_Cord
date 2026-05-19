#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ai_extension.py

실시간 NILM 판단용 AI 확장 모듈

역할:
1. 실시간 ch0/ch1 ADC 파형을 block feature로 변환
2. 최근 WINDOW_SIZE개 block을 모아 학습 때와 같은 window feature 생성
3. state 모델로 empty / plugged_off / on 판단
4. state == on일 때만 device 모델로 charger / cooker / dryer / fan 판단

필요한 모델 파일:
../Model/rf_state_classifier.joblib
../Model/rf_state_features.json
../Model/rf_device_classifier.joblib
../Model/rf_device_features.json

중요:
- 2_make_summary.py, 3_train_state_classifier.py, 4_train_device_classifier.py와 feature 이름이 맞아야 함.
- 학습 때 사용한 feature_names를 json에서 읽어서 순서를 맞춤.
"""

import os
import json
import time
from collections import deque

import joblib
import numpy as np
import pandas as pd


# =========================================================
# 1. 버전 / 경로
# =========================================================

AI_VERSION = "ai_extension_2026_05_20_v38_cooker_off_fast_high_as_dryer"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def find_model_dir():
    """
    모델 폴더 자동 탐색.

    ai_extension.py가 /home/wattsup/Project/kwon/RaspberryPi/NILM 안에 있어도,
    모델은 보통 /home/wattsup/Project/kwon/Model 안에 둘 수 있다.
    그래서 NILM 기준, RaspberryPi 기준, 프로젝트 루트 기준을 모두 확인한다.
    """
    cwd = os.getcwd()

    candidates = [
        os.path.join(BASE_DIR, "Model"),             # .../RaspberryPi/NILM/Model
        os.path.join(BASE_DIR, "..", "Model"),     # .../RaspberryPi/Model
        os.path.join(BASE_DIR, "..", "..", "Model"),  # .../kwon/Model
        os.path.join(cwd, "Model"),
        os.path.join(cwd, "..", "Model"),
        os.path.join(cwd, "..", "..", "Model"),
    ]

    required = [
        "rf_state_classifier.joblib",
        "rf_state_features.json",
        "rf_device_classifier.joblib",
        "rf_device_features.json",
    ]

    checked = []

    for path in candidates:
        path = os.path.abspath(path)
        if path in checked:
            continue
        checked.append(path)

        if os.path.isdir(path) and all(os.path.exists(os.path.join(path, f)) for f in required):
            print(f"[AI MODEL DIR] {path}")
            return path

    print("[AI MODEL DIR ERROR] 모델 폴더를 찾지 못했습니다. 확인한 경로:")
    for path in checked:
        print(f"  - {path}")

    # 에러 메시지를 명확히 하기 위해 프로젝트 루트 후보를 기본값으로 둔다.
    return os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Model"))


MODEL_DIR = find_model_dir()

STATE_MODEL_PATH = os.path.join(MODEL_DIR, "rf_state_classifier.joblib")
STATE_FEATURE_INFO_PATH = os.path.join(MODEL_DIR, "rf_state_features.json")

DEVICE_MODEL_PATH = os.path.join(MODEL_DIR, "rf_device_classifier.joblib")
DEVICE_FEATURE_INFO_PATH = os.path.join(MODEL_DIR, "rf_device_features.json")


# =========================================================
# 2. 실시간 feature 설정
# =========================================================

EPS = 1e-9

USE_PERCENTILE_CLIP = True
CLIP_LOW_PCT = 1
CLIP_HIGH_PCT = 99

# 학습 코드와 맞춰야 함
WINDOW_SIZE_DEFAULT = 10

# state/device 판단 confidence 기준
STATE_ON_MIN_CONF = 0.45
STATE_EMPTY_MIN_CONF = 0.45
DEVICE_MIN_CONF = 0.40

# state 안정화용
STATE_SMOOTH_N = 3
DEVICE_SMOOTH_N = 3

# 너무 자주 출력 바뀌는 것 방지
MIN_PRINT_INTERVAL_SEC = 0.3


# =========================================================
# 3. block feature 컬럼
# =========================================================

BASE_FEATURE_COLS = [
    "Vrms_adc", "Irms_adc", "Vpeak_adc", "Ipeak_adc", "Vpp_adc", "Ipp_adc",
    "Iabs_mean_adc", "Istd_adc", "crest_factor_i",
    "P_proxy", "Pabs_mean_proxy", "Ppeak_proxy", "Pstd_proxy",
    "H1_60_mag", "H3_180_mag", "H5_300_mag", "H7_420_mag",
    "THD_i", "H3_ratio", "H5_ratio", "H7_ratio",
    "fft_peak_freq", "fft_peak_mag",
]


# =========================================================
# 4. feature 계산 함수
# =========================================================

def preprocess_block(x):
    """
    ADC block 전처리
    - percentile clip으로 튀는 값 완화
    - 평균 제거로 DC offset 제거
    """
    x = np.asarray(x, dtype=np.float64)

    if len(x) == 0:
        return x

    if USE_PERCENTILE_CLIP:
        lo = np.percentile(x, CLIP_LOW_PCT)
        hi = np.percentile(x, CLIP_HIGH_PCT)

        if lo < hi:
            x = np.clip(x, lo, hi)

    x = x - np.mean(x)

    return x


def compute_block_features(ch0_block, ch1_block, fs):
    """
    학습용 2_make_summary.py와 같은 block feature 계산

    ch0_block: 전압 ADC raw
    ch1_block: 전류 ADC raw
    fs: sampling frequency
    """
    c0 = preprocess_block(ch0_block)
    c1 = preprocess_block(ch1_block)

    vrms = float(np.sqrt(np.mean(c0 ** 2))) if len(c0) > 0 else 0.0
    irms = float(np.sqrt(np.mean(c1 ** 2))) if len(c1) > 0 else 0.0

    vpeak = float(np.max(np.abs(c0))) if len(c0) > 0 else 0.0
    ipeak = float(np.max(np.abs(c1))) if len(c1) > 0 else 0.0

    vpp = float(np.max(c0) - np.min(c0)) if len(c0) > 0 else 0.0
    ipp = float(np.max(c1) - np.min(c1)) if len(c1) > 0 else 0.0

    iabs_mean = float(np.mean(np.abs(c1))) if len(c1) > 0 else 0.0
    istd = float(np.std(c1)) if len(c1) > 0 else 0.0
    crest_factor_i = float(ipeak / irms) if irms > EPS else 0.0

    p_inst = c0 * c1

    p_proxy = float(np.mean(p_inst)) if len(p_inst) > 0 else 0.0
    pabs_mean_proxy = float(np.mean(np.abs(p_inst))) if len(p_inst) > 0 else 0.0
    ppeak_proxy = float(np.max(np.abs(p_inst))) if len(p_inst) > 0 else 0.0
    pstd_proxy = float(np.std(p_inst)) if len(p_inst) > 0 else 0.0

    h1 = h3 = h5 = h7 = thd = 0.0
    h3_ratio = h5_ratio = h7_ratio = 0.0
    fft_peak_freq = 0.0
    fft_peak_mag = 0.0

    if len(c1) > 16 and fs > 0:
        x = c1 - np.mean(c1)
        xw = x * np.hanning(len(x))

        mags = np.abs(np.fft.rfft(xw))
        freqs = np.fft.rfftfreq(len(xw), d=1.0 / fs)

        def get_mag(target_freq):
            idx = int(np.argmin(np.abs(freqs - target_freq)))
            return float(mags[idx])

        h1 = get_mag(60.0)
        h3 = get_mag(180.0)
        h5 = get_mag(300.0)
        h7 = get_mag(420.0)

        if h1 > EPS:
            thd = float(np.sqrt(h3 ** 2 + h5 ** 2 + h7 ** 2) / h1)
            h3_ratio = float(h3 / h1)
            h5_ratio = float(h5 / h1)
            h7_ratio = float(h7 / h1)

        valid = freqs >= 60.0

        if np.any(valid):
            valid_freqs = freqs[valid]
            valid_mags = mags[valid]
            peak_idx = int(np.argmax(valid_mags))
            fft_peak_freq = float(valid_freqs[peak_idx])
            fft_peak_mag = float(valid_mags[peak_idx])

    return {
        "Vrms_adc": vrms,
        "Irms_adc": irms,
        "Vpeak_adc": vpeak,
        "Ipeak_adc": ipeak,
        "Vpp_adc": vpp,
        "Ipp_adc": ipp,
        "Iabs_mean_adc": iabs_mean,
        "Istd_adc": istd,
        "crest_factor_i": crest_factor_i,

        "P_proxy": p_proxy,
        "Pabs_mean_proxy": pabs_mean_proxy,
        "Ppeak_proxy": ppeak_proxy,
        "Pstd_proxy": pstd_proxy,

        "H1_60_mag": h1,
        "H3_180_mag": h3,
        "H5_300_mag": h5,
        "H7_420_mag": h7,
        "THD_i": thd,
        "H3_ratio": h3_ratio,
        "H5_ratio": h5_ratio,
        "H7_ratio": h7_ratio,
        "fft_peak_freq": fft_peak_freq,
        "fft_peak_mag": fft_peak_mag,
    }


def make_window_features_from_blocks(block_rows, required_feature_names):
    """
    최근 block feature 여러 개를 학습 때와 같은 window feature로 변환

    학습 코드에서 feature 이름은 예를 들면:
    Irms_adc_mean
    Irms_adc_std
    Irms_adc_min
    Irms_adc_max

    json에 저장된 required_feature_names 순서대로 DataFrame 1행 생성
    """
    df = pd.DataFrame(list(block_rows))

    feat = {}

    for col in BASE_FEATURE_COLS:
        if col not in df.columns:
            values = pd.Series([], dtype=float)
        else:
            values = pd.to_numeric(df[col], errors="coerce")
            values = values.replace([np.inf, -np.inf], np.nan).dropna()

        feat[f"{col}_mean"] = float(values.mean()) if len(values) else 0.0
        feat[f"{col}_std"] = float(values.std(ddof=0)) if len(values) else 0.0
        feat[f"{col}_min"] = float(values.min()) if len(values) else 0.0
        feat[f"{col}_max"] = float(values.max()) if len(values) else 0.0

    # 모델이 요구하는 feature만, 정확한 순서로 맞춤
    row = {}

    for name in required_feature_names:
        row[name] = feat.get(name, 0.0)

    X = pd.DataFrame([row], columns=required_feature_names)
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    return X


# =========================================================
# 5. 유틸 함수
# =========================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def predict_with_proba(model, X, labels_from_json=None):
    """
    sklearn model 예측 + 확률 반환
    """
    pred = model.predict(X)[0]

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        classes = list(model.classes_)

        prob_dict = {
            str(cls): float(p)
            for cls, p in zip(classes, proba)
        }

        conf = float(prob_dict.get(str(pred), 0.0))
    else:
        prob_dict = {}
        conf = 1.0

    if labels_from_json is not None:
        for label in labels_from_json:
            prob_dict.setdefault(str(label), 0.0)

    return str(pred), conf, prob_dict


def majority_vote(items):
    """
    items: list of string
    """
    if not items:
        return None

    counts = {}

    for x in items:
        counts[x] = counts.get(x, 0) + 1

    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[0][0]


def format_prob_dict(prob_dict, topk=4):
    if not prob_dict:
        return ""

    items = sorted(prob_dict.items(), key=lambda kv: kv[1], reverse=True)
    items = items[:topk]

    return ", ".join([f"{k}={v:.2f}" for k, v in items])


# =========================================================
# 6. NILM AI Extension 클래스
# =========================================================

class NILMAIExtension:
    def __init__(
        self,
        state_model_path=STATE_MODEL_PATH,
        state_feature_info_path=STATE_FEATURE_INFO_PATH,
        device_model_path=DEVICE_MODEL_PATH,
        device_feature_info_path=DEVICE_FEATURE_INFO_PATH,
        verbose=True,
    ):
        self.verbose = verbose

        self.state_model_path = state_model_path
        self.state_feature_info_path = state_feature_info_path
        self.device_model_path = device_model_path
        self.device_feature_info_path = device_feature_info_path

        self.state_model = None
        self.device_model = None

        self.state_info = None
        self.device_info = None

        self.state_feature_names = []
        self.device_feature_names = []

        self.state_labels = []
        self.device_labels = []

        self.window_size = WINDOW_SIZE_DEFAULT

        self.block_buffer = deque(maxlen=WINDOW_SIZE_DEFAULT)

        self.state_history = deque(maxlen=STATE_SMOOTH_N)
        self.device_history = deque(maxlen=DEVICE_SMOOTH_N)

        self.last_result = None
        self.last_print_time = 0.0

        self.load_models()

    def load_models(self):
        """
        state/device 모델과 feature json 로드
        """
        print(f"[AI VERSION] {AI_VERSION}")

        if not os.path.exists(self.state_model_path):
            raise FileNotFoundError(f"state model not found: {self.state_model_path}")

        if not os.path.exists(self.state_feature_info_path):
            raise FileNotFoundError(f"state feature json not found: {self.state_feature_info_path}")

        if not os.path.exists(self.device_model_path):
            raise FileNotFoundError(f"device model not found: {self.device_model_path}")

        if not os.path.exists(self.device_feature_info_path):
            raise FileNotFoundError(f"device feature json not found: {self.device_feature_info_path}")

        self.state_model = joblib.load(self.state_model_path)
        self.device_model = joblib.load(self.device_model_path)

        self.state_info = load_json(self.state_feature_info_path)
        self.device_info = load_json(self.device_feature_info_path)

        self.state_feature_names = list(self.state_info.get("feature_names", []))
        self.device_feature_names = list(self.device_info.get("feature_names", []))

        self.state_labels = list(self.state_info.get("class_labels", []))
        self.device_labels = list(self.device_info.get("class_labels", []))

        state_window_size = int(self.state_info.get("window_size", WINDOW_SIZE_DEFAULT))
        device_window_size = int(self.device_info.get("window_size", WINDOW_SIZE_DEFAULT))

        self.window_size = max(state_window_size, device_window_size, WINDOW_SIZE_DEFAULT)
        self.block_buffer = deque(maxlen=self.window_size)

        print("[AI INIT] state_model =", self.state_model_path)
        print("[AI INIT] device_model =", self.device_model_path)
        print("[AI INIT] state_classes =", self.state_labels)
        print("[AI INIT] device_classes =", self.device_labels)
        print("[AI INIT] state_feature_count =", len(self.state_feature_names))
        print("[AI INIT] device_feature_count =", len(self.device_feature_names))
        print("[AI INIT] window_size =", self.window_size)

    def reset(self):
        self.block_buffer.clear()
        self.state_history.clear()
        self.device_history.clear()
        self.last_result = None
        self.last_print_time = 0.0

    def process_block_features(self, block_features):
        """
        이미 계산된 block feature를 입력받아 판단.
        외부 코드에서 feature를 직접 계산하는 구조면 이 함수를 쓰면 됨.
        """
        self.block_buffer.append(block_features)

        if len(self.block_buffer) < self.window_size:
            return {
                "ready": False,
                "reason": f"warming_up {len(self.block_buffer)}/{self.window_size}",
                "state": "warming_up",
                "state_conf": 0.0,
                "state_probs": {},
                "device": None,
                "device_conf": 0.0,
                "device_probs": {},
                "block_features": block_features,
            }

        return self._predict_current(block_features)

    def process_samples(self, ch0_block, ch1_block, fs):
        """
        실시간 raw ADC block을 입력받아 판단.
        main 코드에서 SPI로 받은 ch0/ch1 배열을 이 함수에 넣으면 됨.

        ch0_block: voltage ADC samples
        ch1_block: current ADC samples
        fs: sampling frequency
        """
        block_features = compute_block_features(ch0_block, ch1_block, fs)
        return self.process_block_features(block_features)

    def _predict_current(self, latest_block_features):
        """
        최근 block buffer를 이용해서 state/device 판단
        """
        X_state = make_window_features_from_blocks(
            self.block_buffer,
            self.state_feature_names,
        )

        raw_state, state_conf, state_probs = predict_with_proba(
            self.state_model,
            X_state,
            labels_from_json=self.state_labels,
        )

        self.state_history.append(raw_state)
        smooth_state = majority_vote(list(self.state_history)) or raw_state

        final_state = self._apply_state_guard(
            raw_state=raw_state,
            smooth_state=smooth_state,
            state_conf=state_conf,
            state_probs=state_probs,
            latest_block_features=latest_block_features,
        )

        device = None
        device_conf = 0.0
        device_probs = {}

        if final_state == "on":
            X_device = make_window_features_from_blocks(
                self.block_buffer,
                self.device_feature_names,
            )

            raw_device, device_conf, device_probs = predict_with_proba(
                self.device_model,
                X_device,
                labels_from_json=self.device_labels,
            )

            self.device_history.append(raw_device)
            smooth_device = majority_vote(list(self.device_history)) or raw_device

            if device_conf >= DEVICE_MIN_CONF:
                device = smooth_device
            else:
                device = "unknown_on"
        else:
            self.device_history.clear()

        result = {
            "ready": True,
            "version": AI_VERSION,

            "state": final_state,
            "raw_state": raw_state,
            "state_conf": float(state_conf),
            "state_probs": state_probs,

            "device": device,
            "device_conf": float(device_conf),
            "device_probs": device_probs,

            "Irms_adc": float(latest_block_features.get("Irms_adc", 0.0)),
            "Pabs_mean_proxy": float(latest_block_features.get("Pabs_mean_proxy", 0.0)),
            "H1_60_mag": float(latest_block_features.get("H1_60_mag", 0.0)),
            "THD_i": float(latest_block_features.get("THD_i", 0.0)),
            "fft_peak_freq": float(latest_block_features.get("fft_peak_freq", 0.0)),

            # DeltaMultiDeviceTracker가 전체 feature 변화를 제대로 볼 수 있도록
            # ready 결과에도 원본 block feature를 반드시 포함한다.
            # 이 값이 빠지면 tracker가 Irms/Pabs/H1/THD/fft_peak_freq 5개만 보고
            # delta device 분류를 하게 되어 dryer가 fan으로 끌리는 문제가 생긴다.
            "block_features": dict(latest_block_features),
        }

        self.last_result = result

        if self.verbose:
            self.print_result(result)

        return result

    def _apply_state_guard(
        self,
        raw_state,
        smooth_state,
        state_conf,
        state_probs,
        latest_block_features,
    ):
        """
        state 모델 결과 보정.

        목적:
        - confidence가 너무 낮으면 갑자기 on/off가 튀는 것 방지
        - empty/plugged_off/on 판단 안정화

        이 guard는 너무 강하게 넣으면 fan LOW가 씹힐 수 있으므로 약하게 둠.
        """
        state = smooth_state

        pabs = float(latest_block_features.get("Pabs_mean_proxy", 0.0))
        irms = float(latest_block_features.get("Irms_adc", 0.0))
        h1 = float(latest_block_features.get("H1_60_mag", 0.0))

        # 확률이 너무 낮으면 raw보다 smoothing 결과 우선
        if raw_state == "on" and state_conf < STATE_ON_MIN_CONF:
            on_prob = float(state_probs.get("on", 0.0))
            empty_prob = float(state_probs.get("empty", 0.0))
            off_prob = float(state_probs.get("plugged_off", 0.0))

            # on 확률이 낮고 empty/off가 더 강하면 on 취소
            if max(empty_prob, off_prob) > on_prob:
                state = "plugged_off" if off_prob >= empty_prob else "empty"

        if raw_state == "empty" and state_conf < STATE_EMPTY_MIN_CONF:
            # empty confidence가 낮으면 smoothing 결과 유지
            state = smooth_state

        # 아주 약한 fan LOW를 살리기 위해 하드 threshold는 세게 걸지 않음.
        # 단, 세 feature가 전부 거의 0이면 empty 쪽으로 보정.
        if pabs < 100.0 and irms < 1.0 and h1 < 10.0:
            state = "empty"

        return state

    def print_result(self, result):
        now = time.time()

        if now - self.last_print_time < MIN_PRINT_INTERVAL_SEC:
            return

        self.last_print_time = now

        if not result.get("ready", False):
            print(f"[AI] {result.get('reason', 'not ready')}")
            return

        state = result["state"]
        raw_state = result["raw_state"]
        state_conf = result["state_conf"]

        device = result["device"]
        device_conf = result["device_conf"]

        irms = result["Irms_adc"]
        pabs = result["Pabs_mean_proxy"]
        h1 = result["H1_60_mag"]
        thd = result["THD_i"]

        state_probs_text = format_prob_dict(result.get("state_probs", {}), topk=3)
        device_probs_text = format_prob_dict(result.get("device_probs", {}), topk=4)

        if state == "on":
            print(
                "[AI] "
                f"STATE={state} raw={raw_state} sconf={state_conf:.2f} | "
                f"DEVICE={device} dconf={device_conf:.2f} | "
                f"I={irms:.2f}, Pabs={pabs:.1f}, H1={h1:.1f}, THD={thd:.3f} | "
                f"state_probs[{state_probs_text}] | "
                f"device_probs[{device_probs_text}]"
            )
        else:
            print(
                "[AI] "
                f"STATE={state} raw={raw_state} sconf={state_conf:.2f} | "
                f"DEVICE=None | "
                f"I={irms:.2f}, Pabs={pabs:.1f}, H1={h1:.1f}, THD={thd:.3f} | "
                f"state_probs[{state_probs_text}]"
            )


# =========================================================
# 7. 외부에서 쉽게 쓰기 위한 전역 함수
# =========================================================

_global_ai = None


def init_ai(verbose=True):
    """
    main 코드에서 처음 한 번 호출
    """
    global _global_ai
    _global_ai = NILMAIExtension(verbose=verbose)
    return _global_ai


def process_samples(ch0_block, ch1_block, fs):
    """
    main 코드에서 매 block마다 호출

    사용 예:
        from ai_extension import init_ai, process_samples

        init_ai()
        result = process_samples(ch0_block, ch1_block, fs)
    """
    global _global_ai

    if _global_ai is None:
        _global_ai = NILMAIExtension(verbose=True)

    return _global_ai.process_samples(ch0_block, ch1_block, fs)


def process_block_features(block_features):
    """
    이미 block feature를 계산하고 있다면 이 함수 사용
    """
    global _global_ai

    if _global_ai is None:
        _global_ai = NILMAIExtension(verbose=True)

    return _global_ai.process_block_features(block_features)





# =========================================================
# 7-1. 기존 main.py 호환용 Adapter + Delta 기반 다중 기기 추적
# =========================================================
# main.py가 아래처럼 가져오는 구조를 유지한다.
#     from ai_extension import AIEngine, AIDashboardUI
#
# 핵심 변경점:
# - NILMAIExtension은 기존처럼 전체 state/device 예측을 수행한다.
# - AIEngine 안에서 DeltaMultiDeviceTracker가 최근 feature 변화량을 추적한다.
# - 전력/전류/60Hz 성분이 크게 증가하면 ON 이벤트, 크게 감소하면 OFF 이벤트로 판단한다.
# - ON 이벤트 때 delta feature를 device 모델에 넣어 어떤 기기가 추가됐는지 추정한다.
# - active_devices 리스트를 유지해 여러 기기를 동시에 UI 슬롯에 표시한다.
#
# 주의:
# - 현재 ch0/ch1 하나만 받는 구조라면 실제 물리적 소켓 번호는 알 수 없다.
# - 아래 Socket 1~4는 "실제 콘센트 번호"라기보다 "현재 감지된 기기 표시 슬롯"이다.
# - 실제 Socket 1/2/3/4를 정확히 맞추려면 소켓별 CT/전류 채널이 필요하다.

try:
    from dsp_engine import DSPEngine
    from dashboard_ui import DashboardUI
except Exception as e:
    DSPEngine = None
    DashboardUI = None
    _ADAPTER_IMPORT_ERROR = e
else:
    _ADAPTER_IMPORT_ERROR = None


# =========================================================
# 7-1-1. Delta 기반 다중 기기 추적 설정값
# =========================================================

# 최근 몇 block을 이전 상태 / 현재 상태 평균으로 볼지
DELTA_OLD_N = 6
DELTA_NEW_N = 3
DELTA_HISTORY_N = DELTA_OLD_N + DELTA_NEW_N + 5

# 이벤트 감지 민감도
# 현재 로그 기준 empty에서도 Pabs가 1800~2400 정도 나왔기 때문에 너무 낮게 잡으면 유령 이벤트가 생긴다.
ON_DELTA_PABS_MIN = 4500.0
ON_DELTA_IRMS_MIN = 8.0
ON_DELTA_H1_MIN = 250.0

OFF_DELTA_PABS_MIN = 4500.0
OFF_DELTA_IRMS_MIN = 8.0
OFF_DELTA_H1_MIN = 250.0

# 이벤트 판정 점수. 아래 3개 조건 중 2개 이상 만족하면 이벤트로 인정.
EVENT_SCORE_MIN = 2

# 이벤트 후 몇 block 동안 재감지 막기
EVENT_COOLDOWN_BLOCKS = 6

# OFF 표시 유지 시간/block 수
OFF_HOLD_BLOCKS = 18

# active device 최대 표시 개수
MAX_ACTIVE_DEVICES = 4

# delta feature로 device 분류할 때 confidence 기준
DELTA_DEVICE_MIN_CONF = 0.35

# =========================================================
# Delta device 보정값
# =========================================================
# 현재 device 모델은 absolute summary feature로 학습된 모델이다.
# 그런데 tracker는 "새로 증가/감소한 변화량(delta)"을 모델에 넣기 때문에
# 학습 분포와 완전히 같지 않다. 특히 dryer처럼 큰 부하가 fan으로 끌리는
# 현상이 생길 수 있어, 변화량 크기 기반 guard를 추가한다.
#
# 아래 값은 이전 실행 로그 기준 대략:
# - fan:   Pabs 약 8k~10k, Irms 약 15~18, H1 약 650~850
# - dryer: Pabs 수만~수십만, Irms 수십~수백 이상, H1 수천~수만
# 으로 분리되는 경향을 이용한다.
USE_DELTA_DEVICE_GUARD = True

DRYER_FORCE_PABS = 60000.0
DRYER_FORCE_IRMS = 100.0
DRYER_FORCE_H1 = 5000.0

DRYER_WEAK_PABS = 30000.0
DRYER_WEAK_IRMS = 55.0
DRYER_WEAK_H1 = 2500.0

# v22: fast_high 위에서 FAN OFF/ON delta가 Pabs 18k 근처로 튀는 경우가 있어 여유를 둔다.
FAN_MAX_PABS = 22000.0
FAN_MAX_IRMS = 32.0
FAN_MAX_H1 = 1400.0

# =========================================================
# v3 fan 유령 이벤트 방지 / 복구 설정
# =========================================================
# fan은 dryer보다 변화량이 작아서 노이즈나 드라이기 안정화 흔들림을
# fan ON/OFF로 착각하기 쉽다. 따라서 fan은 즉시 active에 넣지 않고
# pending 상태로 둔 뒤, 이후 몇 block에서 실제 fan 조건이 유지될 때만 확정한다.
FAN_PENDING_TTL_BLOCKS = 10
FAN_PENDING_CONFIRM_HITS = 2
FAN_ON_MIN_ON_PROB = 0.35
FAN_ON_MIN_ABS_CONF = 0.75

# plugged_off 상태에서 fan처럼 보이는 약한 이벤트가 생기는 것을 막는다.
# 단 dryer급 큰 이벤트는 state가 늦게 따라와도 허용한다.
BLOCK_WEAK_ON_WHEN_NOT_ON = True

# fan이 아직 켜져 있다고 볼 수 있는 최소 절대 feature 범위
FAN_ALIVE_PABS_MIN = 6500.0
FAN_ALIVE_IRMS_MIN = 12.0
FAN_ALIVE_H1_MIN = 450.0
FAN_ALIVE_PABS_MAX = 30000.0
FAN_ALIVE_IRMS_MAX = 55.0
FAN_ALIVE_H1_MAX = 2500.0

# OFF로 잘못 제거된 직후 absolute 모델이 fan을 계속 강하게 보면 복구한다.
RECENT_OFF_MEMORY_BLOCKS = 35
FAN_RECOVERY_HITS = 2
FAN_RECOVERY_MIN_CONF = 0.85
FAN_RECOVERY_MIN_ON_PROB = 0.60

# v4: 드라이기 강/약 전환을 OFF로 착각하지 않도록 하는 설정
# 로그상 드라이기 약풍/저출력도 Pabs 20만대, Irms 400 근처, H1 2만 근처로
# empty/fan과는 크기가 완전히 다르다. 따라서 dryer active 상태에서 음수 delta가 나와도
# 현재 absolute feature가 dryer급이면 OFF가 아니라 모드 변경으로 본다.
DRYER_ALIVE_PABS_MIN = 30000.0
DRYER_ALIVE_IRMS_MIN = 55.0
DRYER_ALIVE_H1_MIN = 2500.0
DRYER_RECOVERY_HITS = 1
DRYER_RECOVERY_MIN_CONF = 0.70
DRYER_RECOVERY_MIN_ON_PROB = 0.50

# v4: 드라이기 동작 중 fan 추가는 absolute 모델이 dryer로 유지될 수 있으므로
# fan-sized delta가 충분히 강하면 pending 확인을 더 빠르게 통과시킨다.
FAN_PENDING_CONFIRM_HITS_WHEN_DRYER_ACTIVE = 2
FAN_PENDING_MIN_CONF_WHEN_DRYER_ACTIVE = 0.75

# 같은 기기가 다시 켜졌을 때 기존 slot을 재사용하기 위한 메모리
USE_DEVICE_SLOT_MEMORY = True

# v6: 드라이기 플러그/접점 순간 스파이크를 ON으로 확정하지 않기 위한 보정
# state 모델이 아직 on을 충분히 보고 있지 않은 dryer 이벤트는 바로 표시하지 않고,
# 이후 absolute model이 dryer를 안정적으로 볼 때만 active로 동기화한다.
DRYER_ON_REQUIRE_ON_PROB = 0.60
DRYER_ABS_SYNC_MIN_CONF = 0.85
DRYER_ABS_SYNC_MIN_ON_PROB = 0.80

# v15: 드라이기 인식 지연 완화.
# state_model이 on_prob를 0.48~0.50 근처에서 오래 머물러도,
# feature 자체가 명백히 dryer급이고 abs/device가 dryer 쪽이면 빠르게 DRYER_ON으로 동기화한다.
DRYER_FAST_SYNC_MIN_ON_PROB = 0.45
DRYER_FAST_SYNC_MIN_CONF = 0.45
DRYER_FAST_SYNC_HITS_REQUIRED = 2
# v22: slow_low dryer 단독 구간이 Pabs 34k~38k, I 63~67, H1 2900 근처로 잡혀
# 기존 fast sync 기준(45k/70/3000)을 통과하지 못해 첫 인식이 EMPTY로 남는 문제가 있었다.
# fan 단독 영역(Pabs 9k, I 16~18, H1 800)과는 충분히 떨어져 있으므로 dryer low 기준까지 포함한다.
DRYER_FAST_SYNC_PABS_MIN = 30000.0
DRYER_FAST_SYNC_IRMS_MIN = 55.0
DRYER_FAST_SYNC_H1_MIN = 2500.0

# v15: 고출력 dryer 위에서는 fan 추가분이 Pabs에서 음수/작은 양수로 보이기도 한다.
# 따라서 Pabs 하나만 보지 않고 I/H1 축을 중심으로 fan 후보를 살린다.
HIGH_DRYER_FAN_MIN_CONF = 0.78
HIGH_DRYER_FAN_I_MIN = 6.0
HIGH_DRYER_FAN_I_MAX = 35.0
HIGH_DRYER_FAN_H1_MIN = 250.0
HIGH_DRYER_FAN_H1_MAX = 3200.0
HIGH_DRYER_FAN_PABS_ABS_MAX = 26000.0
HIGH_DRYER_FAN_HITS_REQUIRED = 1

# v36: COOKER_ON + DRYER_ON 위에서 선풍기를 추가할 때 로그상
# 1) dPabs≈14489, dI≈9.4, dH1≈-453, fan_conf≈0.69
# 2) dPabs≈45287, dI≈14.5, dH1≈-1215, fan_conf≈0.71
# 두 패턴 모두 실제 FAN_ON 후보였는데, v35에서는 conf/Pabs 기준 때문에 잘렸다.
# 그래서 high-dryer fan overlay 예외만 완화한다.
HIGH_DRYER_FAN_RELAXED_PABS_ABS_MAX = 52000.0
HIGH_DRYER_FAN_RELAXED_I_ABS_MAX = 35.0
HIGH_DRYER_FAN_RELAXED_H1_MIN = 150.0
HIGH_DRYER_FAN_RELAXED_MIN_CONF = 0.68

# v35: COOKER_ON + DRYER_ON 상태에서 dryer fast_high 흔들림이
# 작은 OFF COOKER 후보로 잡히는 것을 차단한다.
COOKER_DRYER_FALSE_COOKER_OFF_PABS_MAX = 50000.0
COOKER_DRYER_FALSE_COOKER_OFF_IRMS_MAX = 60.0
COOKER_DRYER_FALSE_COOKER_OFF_H1_MAX = 2500.0

# v37: COOKER_ON 상태에서 DRYER_ON이 막 추가된 직후에는
# dryer fast_high 램프/안정화가 큰 음수 delta로 나타나 COOKER_OFF로 오인될 수 있다.
# 이 구간은 짧게 보호해서 3기기 진입 전에 cooker가 먼저 꺼지는 것을 막는다.
COOKER_DRYER_ENTRY_GUARD_BLOCKS = 35

# v37: COOKER+DRYER+FAN 상태에서 fast_high dryer 흔들림이 작은 FAN_OFF로 선택되는 문제 방지.
# 진짜 fan off보다 H1 변화가 너무 작거나 dryer 고출력 잔류가 강하면 우선 dryer fluctuation으로 본다.
THREE_ON_WEAK_FAN_OFF_PABS_MAX = 65000.0
THREE_ON_WEAK_FAN_OFF_IRMS_MAX = 25.0
THREE_ON_WEAK_FAN_OFF_H1_MAX = 900.0

# v6: idle 수준으로 내려왔는데 active fan/dryer가 남아 있는 stale 상태 제거
IDLE_CLEAR_PABS_MAX = 4500.0
IDLE_CLEAR_IRMS_MAX = 8.0
IDLE_CLEAR_H1_MAX = 180.0

# =========================================================
# v7: signature stack 예외 로직 강화
# =========================================================
# 핵심 목적:
# 1) 플러그 꽂는 순간 스파이크를 실제 ON으로 확정하지 않음
# 2) 드라이기 출력 변화(강/약/램프업)를 FAN 추가로 착각하지 않음
# 3) 전체 feature가 idle로 내려가면 active stack을 강제로 정리함
# 4) active dryer가 있을 때 fan 추가는 매우 보수적으로만 허용함

# dryer가 active일 때 fan 후보를 확정하기 위한 훨씬 엄격한 delta 범위
FAN_WITH_DRYER_MAX_PABS = 24000.0
FAN_WITH_DRYER_MAX_IRMS = 36.0
FAN_WITH_DRYER_MAX_H1 = 1700.0
FAN_WITH_DRYER_MIN_CONF = 0.80
FAN_WITH_DRYER_REQUIRED_HITS = 3

# absolute model이 dryer를 강하게 보고 있으면 pending fan을 제거
DRYER_DOMINANT_CANCEL_CONF = 0.80
DRYER_DOMINANT_CANCEL_FAN_PROB_MAX = 0.20

# 플러그/접점 스파이크 방지: dryer delta가 나온 직후 latest가 idle이면 ON 확정 금지
DEFER_DRYER_UNTIL_STABLE_ON = True

# active에 fan이 있는데 현재 값이 idle인 block이 연속으로 나오면 강제 제거
IDLE_CLEAR_HITS_REQUIRED = 2

# =========================================================
# v8: dryer baseline residual 기반 FAN 복구/추가 감지
# =========================================================
# v7에서는 드라이기 변동을 fan으로 오검출하는 것을 막기 위해 매우 보수적으로 막았지만,
# 실제 fan 추가분까지 막히는 문제가 있었다.
# v8은 DRYER_ON 안정 구간의 baseline을 저장하고, 현재값 - dryer_baseline 잔차가
# fan 크기로 여러 block 지속될 때만 FAN_ON을 복구/추가한다.
DRYER_BASELINE_BLOCKS = 8
DRYER_BASELINE_MIN_BLOCKS = 5
DRYER_BASELINE_ABS_CONF_MIN = 0.88
DRYER_BASELINE_ON_PROB_MIN = 0.90

FAN_RESIDUAL_PABS_MIN = 2000.0
FAN_RESIDUAL_IRMS_MIN = 4.5
FAN_RESIDUAL_H1_MIN = 250.0
FAN_RESIDUAL_PABS_MAX = 20000.0
FAN_RESIDUAL_IRMS_MAX = 36.0
FAN_RESIDUAL_H1_MAX = 1900.0
FAN_RESIDUAL_HITS_REQUIRED = 2

# v14: 드라이기 출력이 큰 구간에서는 fan 추가분이 baseline 갱신에 흡수되거나
# 드라이기 출력 흔들림과 섞여 strong residual 조건을 놓칠 수 있다.
# 따라서 약한 fan-like residual은 baseline 갱신을 잠깐 freeze하고, 더 긴 연속 확인 후 FAN_ON으로 확정한다.
FAN_RESIDUAL_SOFT_PABS_MIN = 1800.0
FAN_RESIDUAL_SOFT_IRMS_MIN = 3.8
FAN_RESIDUAL_SOFT_H1_MIN = 150.0
FAN_RESIDUAL_SOFT_PABS_MAX = 30000.0
FAN_RESIDUAL_SOFT_IRMS_MAX = 55.0
FAN_RESIDUAL_SOFT_H1_MAX = 3200.0
FAN_RESIDUAL_SOFT_HITS_REQUIRED = 2
DRYER_BASELINE_FREEZE_BLOCKS = 10

# 드라이기 OFF 이후 fan만 남았을 때 absolute feature로 FAN_ON 복구
POST_DRYER_OFF_FAN_RECOVERY_BLOCKS = 25
POST_DRYER_OFF_FAN_HITS_REQUIRED = 2
POST_DRYER_OFF_FAN_ON_PROB_MIN = 0.45
POST_DRYER_OFF_FAN_ABS_CONF_MIN = 0.55

# v11: DRYER_ON + FAN_ON 상태에서 선풍기를 끄면 전체값은 DRYER baseline 근처로 돌아간다.
# 이때 일반 delta OFF가 드라이기 변동에 묻혀 FAN_OFF를 못 잡을 수 있으므로,
# dryer_baseline 대비 fan 잔차가 사라진 상태가 몇 block 지속되면 FAN_OFF로 처리한다.
FAN_OFF_RESIDUAL_MISSING_HITS_REQUIRED = 2
FAN_OFF_RESIDUAL_ON_PROB_MIN = 0.80
FAN_OFF_RESIDUAL_DRYER_CONF_MIN = 0.70
FAN_OFF_RESIDUAL_PABS_MAX = 1800.0
FAN_OFF_RESIDUAL_IRMS_MAX = 4.0
FAN_OFF_RESIDUAL_H1_MAX = 220.0

# v17: FAN_ON + DRYER_ON 상태에서 absolute 모델이 dryer만 본다는 이유만으로
# FAN을 조용히 삭제하지 않는다. 실제 FAN OFF는 delta/residual missing으로 처리해서
# UI에 FAN_OFF + DRYER_ON 잔상이 남도록 한다.
PROTECT_TRACKED_FAN_WHEN_DRYER_DOMINANT = True

# v17/v19: FAN_OFF 직후에는 dryer baseline 잔차가 흔들려 FAN_ON이 다시 뜨는 ghost recovery를 막는다.
# 단, v19에서는 이 값을 "무조건 차단"으로 쓰지 않고, positive residual이 충분히 지속되면 재ON을 허용한다.
BLOCK_RESIDUAL_FAN_READD_WHEN_RECENTLY_OFF = True
FAN_READD_AFTER_OFF_EXTRA_HITS = 1

# v19: residual이 음수라는 것은 FAN_OFF가 아니라 dryer baseline/출력 모드가 달라졌다는 뜻일 수 있다.
# 특히 로그상 FAN_ON 직후 rPabs=-8047, rI=-16.53, rH1=-921.5를 FAN_OFF로 잘못 처리했다.
# 그래서 음수 residual은 FAN_OFF residual-missing 경로에서 제거하지 않고, delta OFF 이벤트에 맡긴다.
DRYER_MODE_SHIFT_NEG_PABS = 1800.0
DRYER_MODE_SHIFT_NEG_IRMS = 3.8
DRYER_MODE_SHIFT_NEG_H1 = 150.0

# v22: FAN_ON + DRYER_ON에서 fan을 먼저 껐는데 일반 OFF delta가 안 잡히는 경우,
# v19의 negative residual 보호 때문에 FAN_ON이 계속 남을 수 있다.
# 단, 드라이기 강/약 모드 전환 직후에는 같은 음수 residual이 정상적으로 생기므로
# 짧은 guard 시간 동안은 fan off로 처리하지 않는다.
DRYER_MODE_SHIFT_GUARD_BLOCKS = 8
FAN_OFF_NEGATIVE_RESIDUAL_HITS_REQUIRED = 3
FAN_OFF_NEGATIVE_DRYER_CONF_MIN = 0.75
FAN_OFF_NEGATIVE_FAN_PROB_MAX = 0.12

# v18: DRYER_ON 상태에서 FAN을 껐다/켰을 때 슬롯 중복과 재인식 실패를 막기 위한 보정.
# fan OFF는 작은 음수 delta로만 보일 때가 많아 dryer mode change와 구분하기 위해
# fan급 변화량 범위를 별도로 둔다.
FAN_OFF_WITH_DRYER_PABS_MIN = 3500.0
FAN_OFF_WITH_DRYER_PABS_MAX = 30000.0
FAN_OFF_WITH_DRYER_IRMS_MIN = 5.0
FAN_OFF_WITH_DRYER_IRMS_MAX = 55.0
FAN_OFF_WITH_DRYER_H1_MIN = 150.0
FAN_OFF_WITH_DRYER_H1_MAX = 2600.0
FAN_OFF_GRACE_BLOCKS = 5

# FAN_OFF 직후 사용자가 실제로 다시 켜는 경우는 delta ON 이벤트가 fan-sized로 잡힌다.
# 이때 absolute model이 dryer만 강하게 봐도 pending을 취소하지 않는다.
ALLOW_FAN_REON_BY_DELTA_WHILE_DRYER_DOMINANT = True

# v9: fan 단독 absolute sync는 dryer용 sync 기준보다 낮은 on_prob에서 허용한다.
# 로그상 fan 단독은 on_prob가 0.74~0.79, fan_conf가 0.94~0.98인데 기존 코드는
# DRYER_ABS_SYNC_MIN_ON_PROB=0.80을 공용으로 써서 FAN_ON을 놓쳤다.
FAN_ABS_SYNC_MIN_ON_PROB = 0.70
FAN_ABS_SYNC_MIN_CONF = 0.88
FAN_ABS_SYNC_HITS_REQUIRED = 2

# v10: charger active 자체를 막지 않는다. 대신 RF가 애매하게 charger 후보를 올리는 상황을
# 후보 단계에서 차단한다. 즉, charger도 실제로 강하게/일관되게 보이면 active에 올라갈 수 있다.
ALLOW_CHARGER_ACTIVE = True

# charger 후보 신뢰 조건: 단순 conf만 보지 않고 charger 확률이 fan/dryer보다 충분히 우세해야 한다.
# 전체 CT 하나에서는 fan/dryer 혼합 구간에서 charger가 후보로 튀는 경우가 있어서 margin을 둔다.
CHARGER_ACTIVE_MIN_CONF = 0.78
CHARGER_PROB_MARGIN_MIN = 0.18
CHARGER_ABS_SYNC_MIN_CONF = 0.82
CHARGER_ABS_SYNC_MIN_ON_PROB = 0.70
CHARGER_ABS_SYNC_HITS_REQUIRED = 2

# fan 단독 영역과 겹치는 charger 후보는 charger로 확정하지 않는다.
# 로그상 fan 단독: I≈15~17, Pabs≈8400~9600, H1≈730~830 이므로 이 영역이면 fan 우선.
CHARGER_REJECT_FANLIKE_PABS_MIN = 6500.0
CHARGER_REJECT_FANLIKE_PABS_MAX = 12500.0
CHARGER_REJECT_FANLIKE_IRMS_MIN = 11.0
CHARGER_REJECT_FANLIKE_IRMS_MAX = 25.0
CHARGER_REJECT_FANLIKE_H1_MIN = 500.0
CHARGER_REJECT_FANLIKE_H1_MAX = 1200.0


# =========================================================
# v23: cooker(밥솥) 3기기 확장 설정
# =========================================================
# cooker는 측정 데이터상 두 구간이 섞인다.
# - 약한/보온성 구간: I≈20~22, Pabs≈0~10k, H1≈3k
# - 가열 구간: I≈330~350, Pabs≈200k, H1≈45k 이상
# 따라서 단순 크기만으로는 dryer/fan과 겹칠 수 있어,
# RF device 모델이 cooker라고 보는 경우를 우선 살리고,
# OFF/idle/absolute sync 쪽에서 cooker를 별도 active device로 관리한다.
TRACKED_DEVICE_NAMES = ("fan", "dryer", "cooker", "charger")

COOKER_DELTA_MIN_CONF = 0.45
COOKER_ABS_SYNC_MIN_CONF = 0.45
COOKER_ABS_SYNC_MIN_ON_PROB = 0.45
COOKER_ABS_SYNC_HITS_REQUIRED = 2

# cooker alive 판정: 최소 2개 축이 cooker 가능 범위에 들어오면 살아있다고 본다.
COOKER_ALIVE_PABS_MIN = 7000.0
COOKER_ALIVE_IRMS_MIN = 18.0
COOKER_ALIVE_H1_MIN = 2200.0

# cooker가 dryer처럼 큰 가열 구간으로 들어갈 수 있으므로 큰 값 상한은 넓게 둔다.
COOKER_ALIVE_PABS_MAX = 260000.0
COOKER_ALIVE_IRMS_MAX = 430.0
COOKER_ALIVE_H1_MAX = 70000.0

# cooker OFF 후보가 나와도 현재 absolute feature가 여전히 cooker급이면 OFF 취소
COOKER_OFF_CANCEL_MIN_CONF = 0.45

# v24: cooker OFF(플러그만 꽂힘/대기)와 cooker ON(취사/가열)을 분리한다.
# 로그 기준 밥솥을 꽂기만 했을 때도 I≈18~24, Pabs≈7k~11k, H1≈800~1150이 나와
# state/device 모델이 cooker_on으로 오인했다. 취사 버튼 후에는 I≈330~360, Pabs≈200k, H1≈17k 이상으로
# 크게 뛰므로 이 둘을 코드에서 별도 상태로 분리한다.
COOKER_STANDBY_PABS_MIN = 6000.0
COOKER_STANDBY_PABS_MAX = 15000.0
COOKER_STANDBY_IRMS_MIN = 14.0
COOKER_STANDBY_IRMS_MAX = 35.0
COOKER_STANDBY_H1_MIN = 500.0
COOKER_STANDBY_H1_MAX = 1600.0

COOKER_HEATING_PABS_MIN = 50000.0
COOKER_HEATING_IRMS_MIN = 80.0
COOKER_HEATING_H1_MIN = 5000.0
COOKER_HEATING_SCORE_MIN = 2

# 플러그 삽입 순간의 일시적인 cooker spike를 COOKER_ON으로 바로 올리지 않기 위한 조건.
COOKER_ON_REQUIRE_ON_PROB = 0.60
COOKER_ON_REQUIRE_STATE_ON = True

# v26: COOKER_OFF(밥솥 대기) 위에 FAN이 켜진 경우.
# cooker_off 단독은 보통 Pabs 7~11k / I 18~24 / H1 800~1150,
# cooker_off + fan은 Pabs 13~17k / I 24~30 / H1 1100~1450 근처로 올라간다.
# RF absolute 모델은 이 구간도 cooker로 보는 경우가 많으므로, 별도 profile로 FAN_ON을 보정한다.
COOKER_PLUS_FAN_PABS_MIN = 12500.0
COOKER_PLUS_FAN_PABS_MAX = 23000.0
COOKER_PLUS_FAN_IRMS_MIN = 23.0
COOKER_PLUS_FAN_IRMS_MAX = 45.0
COOKER_PLUS_FAN_H1_MIN = 1050.0
COOKER_PLUS_FAN_H1_MAX = 2200.0
COOKER_PLUS_FAN_HITS_REQUIRED = 2

# v28: COOKER_OFF + FAN_ON 상태에서 드라이기 재가동/출력 변경이 크게 일어나면
# 전체 파형이 cooker heating처럼 보이면서 COOKER_ON으로 잘못 승격되는 문제가 있었다.
# 특히 DRYER_OFF 직후 fast_high 재가동, DRYER_ON 상태에서 slow_low -> slow_mid 변경 시
# RF가 cooker를 보더라도 이는 기존 dryer context의 출력 변화로 우선 처리한다.
COOKER_FALSE_ON_DRYER_CONTEXT_PABS_MIN = 30000.0
COOKER_FALSE_ON_DRYER_CONTEXT_IRMS_MIN = 55.0
COOKER_FALSE_ON_DRYER_CONTEXT_H1_MIN = 2500.0

# v29: 특히 dryer fast_high는 cooker heating보다 훨씬 큰 영역으로 튀면서
# RF 모델이 cooker로 오판하는 구간이 있었다.
# COOKER_OFF + FAN_ON/DRYER context에서 이 초고출력 영역은 cooker_on이 아니라
# dryer fast_high/모드 변경으로 우선 처리한다.
COOKER_FALSE_FAST_DRYER_PABS_MIN = 250000.0
COOKER_FALSE_FAST_DRYER_IRMS_MIN = 500.0
COOKER_FALSE_FAST_DRYER_H1_MIN = 20000.0

# v32: DRYER_OFF + FAN_ON + COOKER_OFF 상태에서
# 실제 밥솥 취사 재시작과 드라이기 재가동 램프업을 구분하기 위한
# "진짜 cooker heating" 후보 영역.
# 실제 cooker ON 로그: I≈290~380, Pabs≈160k~230k, H1≈14k~19k
# dryer fast_high 램프업 로그: I≈230, Pabs≈123k, H1≈10.6k 이후 초고출력으로 점프
COOKER_REAL_HEATING_WITH_FAN_PABS_MIN = 140000.0
COOKER_REAL_HEATING_WITH_FAN_PABS_MAX = 280000.0
COOKER_REAL_HEATING_WITH_FAN_IRMS_MIN = 260.0
COOKER_REAL_HEATING_WITH_FAN_IRMS_MAX = 460.0
COOKER_REAL_HEATING_WITH_FAN_H1_MIN = 13000.0
COOKER_REAL_HEATING_WITH_FAN_H1_MAX = 24000.0

# v34: 3기기 ON 상태에서 드라이기 모드 변경을 COOKER/FAN OFF로 오인하지 않기 위한 보호값.
# 실제 cooker OFF라면 cooker heating 크기만큼의 음수 delta가 비교적 크게 나오지만,
# 로그상 mode-change false cooker OFF는 dPabs≈-105k, dI≈-224, dH1≈-10k 수준이었다.
THREE_ON_FALSE_COOKER_OFF_PABS_MAX = 140000.0
THREE_ON_FALSE_COOKER_OFF_IRMS_MAX = 260.0
THREE_ON_FALSE_COOKER_OFF_H1_MAX = 13000.0


# 같은 기기가 이미 active일 때 중복 추가 방지
ALLOW_DUPLICATE_SAME_DEVICE = False

# 너무 작은 delta feature는 0으로 정리
DELTA_EPS = 1e-9

# empty/plugged_off 표시 보정
IDLE_BASELINE_BLOCKS = 15
IDLE_MARGIN_PABS = 1800.0
IDLE_MARGIN_IRMS = 4.0
IDLE_MARGIN_H1 = 120.0


# delta 계산 시 음수가 나오면 0으로 클램프해도 되는 feature들
NONNEGATIVE_FEATURES = set(BASE_FEATURE_COLS)


def _safe_float(x, default=0.0):
    try:
        if x is None:
            return default
        v = float(x)
        if not np.isfinite(v):
            return default
        return v
    except Exception:
        return default


def _mean_features(rows):
    """block feature dict 리스트의 평균 dict 생성."""
    if not rows:
        return {col: 0.0 for col in BASE_FEATURE_COLS}

    out = {}
    for col in BASE_FEATURE_COLS:
        vals = [_safe_float(r.get(col, 0.0)) for r in rows]
        out[col] = float(np.mean(vals)) if vals else 0.0
    return out


def _delta_score(delta):
    """delta feature가 ON/OFF 이벤트로 볼 만큼 큰지 점수화."""
    score = 0
    if abs(_safe_float(delta.get("Pabs_mean_proxy", 0.0))) >= ON_DELTA_PABS_MIN:
        score += 1
    if abs(_safe_float(delta.get("Irms_adc", 0.0))) >= ON_DELTA_IRMS_MIN:
        score += 1
    if abs(_safe_float(delta.get("H1_60_mag", 0.0))) >= ON_DELTA_H1_MIN:
        score += 1
    return score


def _event_direction(delta):
    """
    delta가 양수 방향이면 ON, 음수 방향이면 OFF로 본다.
    Pabs/H1/Irms 중 Pabs를 가장 중요하게 사용한다.
    """
    p = _safe_float(delta.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(delta.get("Irms_adc", 0.0))
    h1 = _safe_float(delta.get("H1_60_mag", 0.0))

    pos = 0
    neg = 0

    if p >= ON_DELTA_PABS_MIN:
        pos += 2
    elif p <= -OFF_DELTA_PABS_MIN:
        neg += 2

    if i >= ON_DELTA_IRMS_MIN:
        pos += 1
    elif i <= -OFF_DELTA_IRMS_MIN:
        neg += 1

    if h1 >= ON_DELTA_H1_MIN:
        pos += 1
    elif h1 <= -OFF_DELTA_H1_MIN:
        neg += 1

    if pos >= EVENT_SCORE_MIN and pos > neg:
        return "on"
    if neg >= EVENT_SCORE_MIN and neg > pos:
        return "off"
    return None



def _event_signature_magnitude(event):
    """
    ON/OFF 이벤트에서 사라지거나 추가된 부하의 대표 크기 추출.
    ON 이벤트는 delta가 양수, OFF 이벤트는 delta가 음수이므로 abs를 사용한다.
    """
    delta = event.get("delta", {}) if event else {}

    return {
        "Pabs_mean_proxy": abs(_safe_float(delta.get("Pabs_mean_proxy", 0.0))),
        "Irms_adc": abs(_safe_float(delta.get("Irms_adc", 0.0))),
        "H1_60_mag": abs(_safe_float(delta.get("H1_60_mag", 0.0))),
    }


def _guard_device_by_delta_size(event, model_device=None, model_conf=0.0):
    """
    delta 크기로 device 모델 결과를 보정한다.

    목적:
    - dryer처럼 큰 부하가 RF device 모델에서 fan으로 오분류되는 상황 방지
    - fan은 작은 부하 영역일 때만 fan 판단을 유지
    - charger/cooker 등은 강제 보정하지 않고 모델 결과를 우선

    반환:
        (guard_device, guard_reason)
        guard_device가 None이면 보정하지 않음.
    """
    if not USE_DELTA_DEVICE_GUARD:
        return None, ""

    sig = _event_signature_magnitude(event)
    p = sig["Pabs_mean_proxy"]
    i = sig["Irms_adc"]
    h1 = sig["H1_60_mag"]

    md = _normalize_device_name(model_device)

    # v23: cooker 모델이 충분히 확신하면 큰 변화량이어도 cooker 후보를 우선 살린다.
    # cooker 가열 구간은 dryer급 변화량과 겹칠 수 있으므로 dryer force보다 먼저 확인한다.
    if md == "cooker" and _safe_float(model_conf, 0.0) >= COOKER_DELTA_MIN_CONF:
        return "cooker", f"cooker_model_pass(Pabs={p:.1f},I={i:.2f},H1={h1:.1f},conf={model_conf:.2f})"

    # 매우 큰 변화량이면 모델이 fan이라고 해도 dryer로 강제한다.
    if p >= DRYER_FORCE_PABS or i >= DRYER_FORCE_IRMS or h1 >= DRYER_FORCE_H1:
        return "dryer", f"force_large_delta(Pabs={p:.1f},I={i:.2f},H1={h1:.1f})"

    # 약한 기준 3개 중 2개 이상 만족해도 dryer로 본다.
    dryer_score = 0
    if p >= DRYER_WEAK_PABS:
        dryer_score += 1
    if i >= DRYER_WEAK_IRMS:
        dryer_score += 1
    if h1 >= DRYER_WEAK_H1:
        dryer_score += 1

    if dryer_score >= 2:
        return "dryer", f"weak_large_delta_score={dryer_score}(Pabs={p:.1f},I={i:.2f},H1={h1:.1f})"

    # fan으로 나온 결과는 변화량이 fan 영역일 때만 그대로 신뢰한다.
    # fan 영역을 넘는 큰 부하인데 모델만 fan이면 unknown으로 만들어 오표시를 줄인다.
    if md == "fan":
        if p <= FAN_MAX_PABS and i <= FAN_MAX_IRMS and h1 <= FAN_MAX_H1:
            return "fan", f"fan_range_ok(Pabs={p:.1f},I={i:.2f},H1={h1:.1f})"

        # v16: DRYER_ON 상태에서 fan을 켜면 전체 전력은 dryer가 지배하지만,
        # delta classifier는 여전히 fan 확률을 높게 낸다.
        # 기존 guard가 여기서 None으로 잘라버리면 _handle_on_event()의
        # high_dryer_axis 예외 로직까지 도달하지 못한다.
        # 따라서 high-dryer fan 축 조건을 만족하는 후보는 일단 fan으로 통과시키고,
        # 실제 active dryer 여부와 최종 확정은 _handle_on_event()에서 판단하게 한다.
        if _is_high_dryer_fan_axis_event(event, model_conf):
            return "fan", f"fan_high_dryer_axis_pass(Pabs={p:.1f},I={i:.2f},H1={h1:.1f})"

        return None, f"fan_range_rejected(Pabs={p:.1f},I={i:.2f},H1={h1:.1f})"

    return None, ""


def _prob_for(probs, name):
    if not probs:
        return 0.0
    name = str(name).lower()
    for k, v in probs.items():
        if str(k).strip().lower().replace("_on", "").replace("_off", "") == name:
            return _safe_float(v, 0.0)
    return 0.0


def _is_fan_like_signature(p, i, h1):
    return (
        CHARGER_REJECT_FANLIKE_PABS_MIN <= p <= CHARGER_REJECT_FANLIKE_PABS_MAX and
        CHARGER_REJECT_FANLIKE_IRMS_MIN <= i <= CHARGER_REJECT_FANLIKE_IRMS_MAX and
        CHARGER_REJECT_FANLIKE_H1_MIN <= h1 <= CHARGER_REJECT_FANLIKE_H1_MAX
    )


def _charger_candidate_quality(probs, conf):
    charger_p = _prob_for(probs, "charger")
    fan_p = _prob_for(probs, "fan")
    dryer_p = _prob_for(probs, "dryer")

    # predict_with_proba의 raw label이 간혹 출력상 prob top과 어긋나는 경우까지 방어한다.
    # charger가 실제 top이 아니거나 fan/dryer와 margin이 작으면 charger 후보로 보지 않는다.
    effective_charger = max(charger_p, _safe_float(conf, 0.0) if charger_p <= 0.0 else charger_p)
    rival = max(fan_p, dryer_p)
    margin = effective_charger - rival
    ok = effective_charger >= CHARGER_ACTIVE_MIN_CONF and margin >= CHARGER_PROB_MARGIN_MIN
    return ok, effective_charger, fan_p, dryer_p, margin


def _charger_delta_candidate_is_reliable(event, probs, conf):
    if not ALLOW_CHARGER_ACTIVE:
        return False, "charger_disabled"

    sig = _event_signature_magnitude(event)
    p = sig["Pabs_mean_proxy"]
    i = sig["Irms_adc"]
    h1 = sig["H1_60_mag"]

    if _is_dryer_sized_event(event):
        return False, f"dryer_sized_delta(Pabs={p:.1f},I={i:.2f},H1={h1:.1f})"

    if _is_fan_like_signature(p, i, h1):
        return False, f"fan_like_signature(Pabs={p:.1f},I={i:.2f},H1={h1:.1f})"

    ok, cp, fp, dp, margin = _charger_candidate_quality(probs, conf)
    if not ok:
        return False, f"weak_charger_prob(charger={cp:.2f},fan={fp:.2f},dryer={dp:.2f},margin={margin:.2f})"

    return True, f"charger_candidate_ok(charger={cp:.2f},fan={fp:.2f},dryer={dp:.2f},margin={margin:.2f})"


def _charger_absolute_candidate_is_reliable(latest, probs, conf, on_prob):
    if not ALLOW_CHARGER_ACTIVE:
        return False, "charger_disabled"

    if on_prob < CHARGER_ABS_SYNC_MIN_ON_PROB:
        return False, f"low_on_prob({on_prob:.2f})"

    p = _safe_float(latest.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(latest.get("Irms_adc", 0.0))
    h1 = _safe_float(latest.get("H1_60_mag", 0.0))

    if _is_dryer_alive_features(latest):
        return False, f"dryer_alive_feature(Pabs={p:.1f},I={i:.2f},H1={h1:.1f})"

    if _is_fan_alive_features(latest) or _is_fan_like_signature(p, i, h1):
        return False, f"fan_like_absolute(Pabs={p:.1f},I={i:.2f},H1={h1:.1f})"

    ok, cp, fp, dp, margin = _charger_candidate_quality(probs, max(conf, CHARGER_ABS_SYNC_MIN_CONF))
    if not ok:
        return False, f"weak_charger_abs_prob(charger={cp:.2f},fan={fp:.2f},dryer={dp:.2f},margin={margin:.2f})"

    return True, f"charger_absolute_ok(charger={cp:.2f},fan={fp:.2f},dryer={dp:.2f},margin={margin:.2f})"


def _should_block_charger_active(conf=0.0):
    """v10: active 자체 차단용이 아니라 최저 confidence 방어만 수행한다."""
    if not ALLOW_CHARGER_ACTIVE:
        return True
    return _safe_float(conf, 0.0) < CHARGER_ACTIVE_MIN_CONF


def _normalize_device_name(device):
    if device is None:
        return None

    d = str(device).strip().lower()

    if d in ["", "none", "unknown", "unknown_on", "nan"]:
        return None

    # device 모델이 dryer_on/fan_off처럼 학습된 경우 방어
    d = d.replace("_on", "").replace("_off", "")
    return d


def _is_dryer_sized_event(event):
    """변화량이 dryer급이면 state가 늦게 따라와도 강한 ON/OFF 이벤트로 허용."""
    sig = _event_signature_magnitude(event)
    p = sig["Pabs_mean_proxy"]
    i = sig["Irms_adc"]
    h1 = sig["H1_60_mag"]

    if p >= DRYER_FORCE_PABS or i >= DRYER_FORCE_IRMS or h1 >= DRYER_FORCE_H1:
        return True

    score = 0
    if p >= DRYER_WEAK_PABS:
        score += 1
    if i >= DRYER_WEAK_IRMS:
        score += 1
    if h1 >= DRYER_WEAK_H1:
        score += 1

    return score >= 2


def _is_fan_sized_event(event):
    """ON/OFF 변화량이 fan 영역에 들어오는지 확인."""
    sig = _event_signature_magnitude(event)
    p = sig["Pabs_mean_proxy"]
    i = sig["Irms_adc"]
    h1 = sig["H1_60_mag"]

    return (
        p <= FAN_MAX_PABS and
        i <= FAN_MAX_IRMS and
        h1 <= FAN_MAX_H1 and
        p >= ON_DELTA_PABS_MIN and
        i >= ON_DELTA_IRMS_MIN and
        h1 >= ON_DELTA_H1_MIN
    )


def _is_fan_sized_with_dryer_event(event, conf=0.0):
    """dryer active 상태에서 fan 추가로 인정할 만큼 작은 delta인지 확인."""
    sig = _event_signature_magnitude(event)
    p = sig["Pabs_mean_proxy"]
    i = sig["Irms_adc"]
    h1 = sig["H1_60_mag"]
    return (
        _safe_float(conf, 0.0) >= FAN_WITH_DRYER_MIN_CONF and
        ON_DELTA_PABS_MIN <= p <= FAN_WITH_DRYER_MAX_PABS and
        ON_DELTA_IRMS_MIN <= i <= FAN_WITH_DRYER_MAX_IRMS and
        ON_DELTA_H1_MIN <= h1 <= FAN_WITH_DRYER_MAX_H1
    )


def _is_fan_off_sized_with_dryer_event(event):
    """v18: DRYER_ON 상태에서 FAN_OFF로 볼 수 있는 음수 delta 크기인지 확인.

    OFF 이벤트에서는 event_signature_magnitude()가 abs(delta)를 반환하므로,
    여기서는 fan 1대가 사라졌을 때의 대표 범위만 검사한다.
    dryer 모드 전환급 큰 변화는 이 범위를 벗어나므로 dryer 처리로 넘긴다.
    """
    sig = _event_signature_magnitude(event)
    p = sig["Pabs_mean_proxy"]
    i = sig["Irms_adc"]
    h1 = sig["H1_60_mag"]
    return (
        FAN_OFF_WITH_DRYER_PABS_MIN <= p <= FAN_OFF_WITH_DRYER_PABS_MAX and
        FAN_OFF_WITH_DRYER_IRMS_MIN <= i <= FAN_OFF_WITH_DRYER_IRMS_MAX and
        FAN_OFF_WITH_DRYER_H1_MIN <= h1 <= FAN_OFF_WITH_DRYER_H1_MAX
    )


def _is_high_dryer_fan_axis_event(event, conf=0.0):
    """
    v21: 고출력 dryer 상태에서 fan 추가분은 Pabs/I 축으로는 보이지만,
    H1 변화량은 dryer 자체 흔들림 때문에 음수이거나 250보다 작게 나올 수 있다.

    실제 v20 로그:
      dPabs=18469.1, dI=11.24, dH1=-184.1, fan_conf=0.84
    이 값은 fan ON 후보로 봐야 하는데 기존 조건은 H1_raw >= 250을 요구해서 잘렸다.

    따라서 high-dryer 예외 경로에서는
      1) fan model confidence가 충분히 높고,
      2) Pabs 변화량이 과도하게 크지 않으며,
      3) Irms 변화량이 fan 범위이고,
      4) H1은 방향/최소값보다 절대값 상한만 확인한다.
    """
    if event is None:
        return False

    delta = event.get("delta", {}) or {}
    p_raw = _safe_float(delta.get("Pabs_mean_proxy", 0.0))
    i_raw = _safe_float(delta.get("Irms_adc", 0.0))
    h1_raw = _safe_float(delta.get("H1_60_mag", 0.0))

    p_abs = abs(p_raw)
    h1_abs = abs(h1_raw)

    p_axis_ok = ON_DELTA_PABS_MIN <= p_abs <= HIGH_DRYER_FAN_PABS_ABS_MAX
    i_axis_ok = HIGH_DRYER_FAN_I_MIN <= i_raw <= HIGH_DRYER_FAN_I_MAX
    h1_not_too_large = h1_abs <= HIGH_DRYER_FAN_H1_MAX

    strict_ok = (
        _safe_float(conf, 0.0) >= HIGH_DRYER_FAN_MIN_CONF and
        p_axis_ok and
        i_axis_ok and
        h1_not_too_large
    )
    if strict_ok:
        return True

    # v35: cooker+dryer 고출력 위에 fan을 얹을 때 Irms delta가 작게 보이는 로그 보정.
    # RF가 fan을 강하게 보고, Pabs/H1이 fan 추가 축으로 보이면 I축 최소값을 요구하지 않는다.
    relaxed_ok = (
        _safe_float(conf, 0.0) >= HIGH_DRYER_FAN_RELAXED_MIN_CONF and
        ON_DELTA_PABS_MIN <= p_abs <= HIGH_DRYER_FAN_RELAXED_PABS_ABS_MAX and
        abs(i_raw) <= HIGH_DRYER_FAN_RELAXED_I_ABS_MAX and
        HIGH_DRYER_FAN_RELAXED_H1_MIN <= h1_abs <= HIGH_DRYER_FAN_H1_MAX
    )
    return relaxed_ok


def _is_fast_dryer_sync_features(row):
    """v15: state on_prob가 낮아도 absolute feature가 명백히 dryer급인지 확인."""
    if not row:
        return False
    p = _safe_float(row.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(row.get("Irms_adc", 0.0))
    h1 = _safe_float(row.get("H1_60_mag", 0.0))
    score = 0
    if p >= DRYER_FAST_SYNC_PABS_MIN:
        score += 1
    if i >= DRYER_FAST_SYNC_IRMS_MIN:
        score += 1
    if h1 >= DRYER_FAST_SYNC_H1_MIN:
        score += 1
    return score >= 2


def _is_fast_high_dryer_features(row):
    """v30: fast_high 드라이기처럼 매우 큰 부하 영역인지 확인한다.

    COOKER_OFF + FAN_ON 상태에서 이 영역으로 올라가는 것은
    실제 cooker ON이 아니라 dryer fast_high/모드 변화로 우선 해석한다.
    """
    if not row:
        return False

    p = _safe_float(row.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(row.get("Irms_adc", 0.0))
    h1 = _safe_float(row.get("H1_60_mag", 0.0))

    score = 0
    if p >= COOKER_FALSE_FAST_DRYER_PABS_MIN:
        score += 1
    if i >= COOKER_FALSE_FAST_DRYER_IRMS_MIN:
        score += 1
    if h1 >= COOKER_FALSE_FAST_DRYER_H1_MIN:
        score += 1

    return score >= 2


def _is_real_cooker_heating_with_fan_features(row):
    """v32: COOKER_OFF + FAN_ON + DRYER_OFF 상태에서 실제 cooker 취사 재시작으로 볼 수 있는 영역.

    dryer fast_high 재가동 초반은 cooker처럼 보이지만 보통 첫 구간이
    Pabs/I/H1 모두 이 영역보다 낮거나, 다음 구간에서 초고출력 dryer 영역으로 바로 튄다.
    반대로 실제 cooker 취사는 I≈300~400, Pabs≈160k~230k, H1≈14k~19k 부근에서
    비교적 안정적으로 형성되므로 이 범위를 통과할 때만 COOKER_ON을 허용한다.
    """
    if not row:
        return False

    p = _safe_float(row.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(row.get("Irms_adc", 0.0))
    h1 = _safe_float(row.get("H1_60_mag", 0.0))

    return (
        COOKER_REAL_HEATING_WITH_FAN_PABS_MIN <= p <= COOKER_REAL_HEATING_WITH_FAN_PABS_MAX and
        COOKER_REAL_HEATING_WITH_FAN_IRMS_MIN <= i <= COOKER_REAL_HEATING_WITH_FAN_IRMS_MAX and
        COOKER_REAL_HEATING_WITH_FAN_H1_MIN <= h1 <= COOKER_REAL_HEATING_WITH_FAN_H1_MAX
    )


def _is_fan_alive_features(row):
    """현재 absolute feature가 fan이 실제로 켜져 있을 법한 범위인지 확인."""
    if not row:
        return False

    p = _safe_float(row.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(row.get("Irms_adc", 0.0))
    h1 = _safe_float(row.get("H1_60_mag", 0.0))

    return (
        FAN_ALIVE_PABS_MIN <= p <= FAN_ALIVE_PABS_MAX and
        FAN_ALIVE_IRMS_MIN <= i <= FAN_ALIVE_IRMS_MAX and
        FAN_ALIVE_H1_MIN <= h1 <= FAN_ALIVE_H1_MAX
    )


def _sub_feature_triplet(a, b):
    """a - b 잔차 feature 중 핵심 3개만 반환."""
    return {
        "Pabs_mean_proxy": _safe_float(a.get("Pabs_mean_proxy", 0.0)) - _safe_float(b.get("Pabs_mean_proxy", 0.0)),
        "Irms_adc": _safe_float(a.get("Irms_adc", 0.0)) - _safe_float(b.get("Irms_adc", 0.0)),
        "H1_60_mag": _safe_float(a.get("H1_60_mag", 0.0)) - _safe_float(b.get("H1_60_mag", 0.0)),
    }


def _is_fan_residual_triplet(res):
    """DRYER baseline 위에 얹힌 fan 추가분으로 볼 수 있는 잔차 범위."""
    if not res:
        return False
    p = _safe_float(res.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(res.get("Irms_adc", 0.0))
    h1 = _safe_float(res.get("H1_60_mag", 0.0))
    return (
        FAN_RESIDUAL_PABS_MIN <= p <= FAN_RESIDUAL_PABS_MAX and
        FAN_RESIDUAL_IRMS_MIN <= i <= FAN_RESIDUAL_IRMS_MAX and
        FAN_RESIDUAL_H1_MIN <= h1 <= FAN_RESIDUAL_H1_MAX
    )


def _is_soft_fan_residual_triplet(res):
    """
    v14: 고출력 DRYER 위에서 FAN 추가분이 작게/흔들리게 보일 때 쓰는 완화 조건.
    단일 block으로 확정하지 않고, baseline freeze + 연속 hit 조건에서만 FAN_ON으로 올린다.
    """
    if not res:
        return False
    p = _safe_float(res.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(res.get("Irms_adc", 0.0))
    h1 = _safe_float(res.get("H1_60_mag", 0.0))

    in_box = (
        FAN_RESIDUAL_SOFT_PABS_MIN <= p <= FAN_RESIDUAL_SOFT_PABS_MAX and
        FAN_RESIDUAL_SOFT_IRMS_MIN <= i <= FAN_RESIDUAL_SOFT_IRMS_MAX and
        FAN_RESIDUAL_SOFT_H1_MIN <= h1 <= FAN_RESIDUAL_SOFT_H1_MAX
    )
    if not in_box:
        return False

    # 너무 작은 H1 변화는 드라이기 자체 전력 흔들림일 수 있으므로, 최소 2개 축 이상이 fan-like여야 한다.
    axes = 0
    if p >= FAN_RESIDUAL_PABS_MIN:
        axes += 1
    if i >= FAN_RESIDUAL_IRMS_MIN:
        axes += 1
    if h1 >= FAN_RESIDUAL_H1_MIN:
        axes += 1
    return axes >= 2


def _is_dryer_alive_features(row):
    """현재 absolute feature가 드라이기 동작 중이라고 볼 만큼 큰지 확인."""
    if not row:
        return False

    p = _safe_float(row.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(row.get("Irms_adc", 0.0))
    h1 = _safe_float(row.get("H1_60_mag", 0.0))

    score = 0
    if p >= DRYER_ALIVE_PABS_MIN:
        score += 1
    if i >= DRYER_ALIVE_IRMS_MIN:
        score += 1
    if h1 >= DRYER_ALIVE_H1_MIN:
        score += 1
    return score >= 2


def _is_cooker_alive_features(row):
    """현재 absolute feature가 밥솥 전원 계열이라고 볼 수 있는지 확인.

    주의: v24부터 이 함수는 cooker_off/standby까지 포함한 넓은 cooker 계열 판정이다.
    실제 취사 ON 여부는 _is_cooker_heating_features()로 따로 판단한다.
    """
    if not row:
        return False

    p = _safe_float(row.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(row.get("Irms_adc", 0.0))
    h1 = _safe_float(row.get("H1_60_mag", 0.0))

    score = 0
    if COOKER_ALIVE_PABS_MIN <= p <= COOKER_ALIVE_PABS_MAX:
        score += 1
    if COOKER_ALIVE_IRMS_MIN <= i <= COOKER_ALIVE_IRMS_MAX:
        score += 1
    if COOKER_ALIVE_H1_MIN <= h1 <= COOKER_ALIVE_H1_MAX:
        score += 1

    return score >= 2


def _is_cooker_standby_off_features(row):
    """밥솥을 꽂아만 둔 상태/취사 OFF 상태로 보이는 낮은 cooker profile."""
    if not row:
        return False

    p = _safe_float(row.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(row.get("Irms_adc", 0.0))
    h1 = _safe_float(row.get("H1_60_mag", 0.0))

    return (
        COOKER_STANDBY_PABS_MIN <= p <= COOKER_STANDBY_PABS_MAX and
        COOKER_STANDBY_IRMS_MIN <= i <= COOKER_STANDBY_IRMS_MAX and
        COOKER_STANDBY_H1_MIN <= h1 <= COOKER_STANDBY_H1_MAX
    )


def _is_cooker_heating_features(row):
    """취사/가열 중인 cooker ON profile.

    v26: fan+dryer slow_low 조합도 Pabs/I 축만 보면 cooker heating처럼 보일 수 있었다.
    실제 cooker heating은 H1이 5k 이상으로 같이 올라오므로, 이제 H1 축은 필수로 요구한다.
    """
    if not row:
        return False

    p = _safe_float(row.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(row.get("Irms_adc", 0.0))
    h1 = _safe_float(row.get("H1_60_mag", 0.0))

    return (
        h1 >= COOKER_HEATING_H1_MIN and
        (p >= COOKER_HEATING_PABS_MIN or i >= COOKER_HEATING_IRMS_MIN)
    )


def _is_cooker_plus_fan_features(row):
    """COOKER_OFF 위에 FAN_ON이 얹힌 것으로 보이는 낮은 전력 조합 profile."""
    if not row:
        return False

    p = _safe_float(row.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(row.get("Irms_adc", 0.0))
    h1 = _safe_float(row.get("H1_60_mag", 0.0))

    return (
        COOKER_PLUS_FAN_PABS_MIN <= p <= COOKER_PLUS_FAN_PABS_MAX and
        COOKER_PLUS_FAN_IRMS_MIN <= i <= COOKER_PLUS_FAN_IRMS_MAX and
        COOKER_PLUS_FAN_H1_MIN <= h1 <= COOKER_PLUS_FAN_H1_MAX
    )


def _is_idle_features(row):
    """현재 feature가 사실상 무부하/idle 수준인지 확인한다."""
    if not row:
        return False

    p = _safe_float(row.get("Pabs_mean_proxy", 0.0))
    i = _safe_float(row.get("Irms_adc", 0.0))
    h1 = _safe_float(row.get("H1_60_mag", 0.0))

    return (
        p <= IDLE_CLEAR_PABS_MAX and
        i <= IDLE_CLEAR_IRMS_MAX and
        h1 <= IDLE_CLEAR_H1_MAX
    )


def _event_new_mean_is_dryer_alive(event):
    """이벤트 이후 평균 자체가 이미 dryer급이면, active dryer가 없을 때 fan 후보로 확정하지 않는다."""
    if not event:
        return False
    return _is_dryer_alive_features(event.get("new_mean", {}))


def _event_old_mean_is_dryer_alive(event):
    """이벤트 이전 평균이 dryer급인지 확인한다. dryer 위에 fan이 추가된 경우는 old_mean도 dryer급이어야 한다."""
    if not event:
        return False
    return _is_dryer_alive_features(event.get("old_mean", {}))


def _fan_delta_still_present(pending_event, latest_row):
    """pending fan 이벤트 이후에도 old_mean 대비 fan급 증가분이 유지되는지 확인."""
    if not pending_event or not latest_row:
        return False

    old = pending_event.get("old_mean", {})
    dp = _safe_float(latest_row.get("Pabs_mean_proxy", 0.0)) - _safe_float(old.get("Pabs_mean_proxy", 0.0))
    di = _safe_float(latest_row.get("Irms_adc", 0.0)) - _safe_float(old.get("Irms_adc", 0.0))
    dh = _safe_float(latest_row.get("H1_60_mag", 0.0)) - _safe_float(old.get("H1_60_mag", 0.0))

    return (
        ON_DELTA_PABS_MIN <= dp <= FAN_MAX_PABS and
        ON_DELTA_IRMS_MIN <= di <= FAN_MAX_IRMS and
        ON_DELTA_H1_MIN <= dh <= FAN_MAX_H1
    )


class DeltaMultiDeviceTracker:
    """
    전체 ch0/ch1 한 쌍만 있는 상황에서 다중 기기처럼 보이게 추적하는 이벤트 기반 상태 관리자.

    작동 방식:
    1. 최근 block feature를 저장한다.
    2. 이전 평균 old_mean과 현재 평균 new_mean의 차이를 delta로 계산한다.
    3. delta가 충분히 양수면 새 기기 ON 이벤트로 판단한다.
    4. delta가 충분히 음수면 기존 기기 OFF 이벤트로 판단한다.
    5. ON 이벤트의 delta feature를 device 모델에 넣어 어떤 기기가 추가됐는지 추정한다.
    6. active_devices 리스트를 유지해 여러 기기를 동시에 UI에 표시한다.
    """

    def __init__(self, ai_extension, verbose=True):
        self.ai = ai_extension
        self.verbose = verbose

        self.feature_history = deque(maxlen=DELTA_HISTORY_N)
        self.active_devices = []
        self.off_events = deque(maxlen=MAX_ACTIVE_DEVICES)

        self.cooldown = 0
        self.last_event = None
        self.idle_rows = deque(maxlen=IDLE_BASELINE_BLOCKS)
        self.idle_baseline = None

        # v3: fan 유령 이벤트 방지용 pending/복구 상태
        self.pending_on = None
        self.recent_off_devices = {}
        self.recovery_hits = {}
        self.latest_ai_result = None
        self.latest_features = None
        self.idle_clear_hits = 0
        self.dryer_dominant_fan_false_hits = 0

        # v7 stack reconciliation counters
        self.idle_clear_hits = 0
        self.dryer_dominant_fan_false_hits = 0
        self.device_slot_memory = {}
        # v13: 한 번 식별된 slot은 기기를 OFF 상태로 계속 기억한다.
        #      초기에는 아무 정보가 없으므로 EMPTY지만, 한 번 FAN/DRYER/CHARGER가 잡히면
        #      꺼진 뒤에도 해당 slot은 *_OFF로 유지된다.
        self.retained_off_slots = {}  # slot(int) -> {device, conf, source}

        # v8: dryer baseline residual 기반 fan 감지 상태
        self.dryer_baseline_rows = deque(maxlen=DRYER_BASELINE_BLOCKS)
        self.dryer_baseline = None
        self.dryer_baseline_frozen = None
        self.dryer_baseline_freeze_left = 0
        self.fan_residual_hits = 0
        self.fan_residual_soft_hits = 0
        self.post_dryer_off_recovery_left = 0
        self.post_dryer_off_fan_hits = 0
        self.fan_residual_absent_hits = 0
        self.fan_negative_residual_absent_hits = 0
        self.dryer_mode_shift_guard = 0
        self.cooker_dryer_entry_guard = 0

    def reset(self):
        self.feature_history.clear()
        self.active_devices.clear()
        self.off_events.clear()
        self.cooldown = 0
        self.last_event = None
        self.idle_rows.clear()
        self.idle_baseline = None
        self.pending_on = None
        self.recent_off_devices.clear()
        self.recovery_hits.clear()
        self.latest_ai_result = None
        self.latest_features = None
        self.dryer_baseline_rows.clear()
        self.dryer_baseline = None
        self.dryer_baseline_frozen = None
        self.dryer_baseline_freeze_left = 0
        self.fan_residual_hits = 0
        self.fan_residual_soft_hits = 0
        self.post_dryer_off_recovery_left = 0
        self.post_dryer_off_fan_hits = 0
        self.fan_residual_absent_hits = 0
        self.fan_negative_residual_absent_hits = 0
        self.dryer_mode_shift_guard = 0
        self.cooker_dryer_entry_guard = 0

    def _has_cooker_off_context(self):
        """COOKER_OFF가 이미 식별/표시되고 있는지 확인."""
        if any(x.get("device") == "cooker" for x in self.off_events):
            return True
        if any(info.get("device") == "cooker" for info in self.retained_off_slots.values()):
            return True
        return False

    def _has_dryer_context(self):
        """DRYER가 현재 켜져 있거나, 직전에 OFF로 기억된 상황인지 확인."""
        if any(x.get("device") == "dryer" for x in self.active_devices):
            return True
        if any(x.get("device") == "dryer" for x in self.off_events):
            return True
        if any(info.get("device") == "dryer" for info in self.retained_off_slots.values()):
            return True
        if "dryer" in self.recent_off_devices:
            return True
        return False

    def _has_fan_on_context(self):
        """FAN_ON이 현재 active stack에 있는지 확인."""
        return any(x.get("device") == "fan" and x.get("state") == "on" for x in self.active_devices)

    def _has_three_on_context(self):
        """COOKER/FAN/DRYER가 모두 ON으로 추적 중인지 확인."""
        return (
            any(x.get("device") == "cooker" and x.get("state") == "on" for x in self.active_devices) and
            any(x.get("device") == "fan" and x.get("state") == "on" for x in self.active_devices) and
            any(x.get("device") == "dryer" and x.get("state") == "on" for x in self.active_devices)
        )

    def _has_cooker_dryer_on_context(self):
        """v35: COOKER_ON과 DRYER_ON이 동시에 추적 중인지 확인."""
        return (
            any(x.get("device") == "cooker" and x.get("state") == "on" for x in self.active_devices) and
            any(x.get("device") == "dryer" and x.get("state") == "on" for x in self.active_devices)
        )

    def _should_block_false_cooker_off_during_cooker_dryer_mode_change(self, event, latest):
        """v35: 선풍기 추가 전 COOKER_ON + DRYER_ON 상태에서도 작은 COOKER_OFF 오판을 막는다.

        v34 보호는 3기기 ON에서만 작동해서, COOKER_ON + DRYER_ON 상태에서
        dryer fast_high 흔들림이 OFF COOKER로 들어오면 선풍기 ON 테스트 전에
        COOKER_OFF로 무너지는 문제가 있었다.
        """
        if event is None or not latest:
            return False
        if not self._has_cooker_dryer_on_context():
            return False
        if not _is_dryer_alive_features(latest):
            return False
        if _is_cooker_standby_off_features(latest):
            return False

        delta = event.get("delta", {}) or {}
        d_p_raw = _safe_float(delta.get("Pabs_mean_proxy", 0.0))
        d_i_raw = _safe_float(delta.get("Irms_adc", 0.0))
        d_h1_raw = _safe_float(delta.get("H1_60_mag", 0.0))
        d_p = abs(d_p_raw)
        d_i = abs(d_i_raw)
        d_h1 = abs(d_h1_raw)

        # v37: DRYER_ON 직후 안정화 구간에서는 꽤 큰 음수 delta도 cooker OFF가 아니라
        # dryer fast_high/ramp settling으로 나올 수 있다. 이때는 cooker를 먼저 잃지 않도록 보호한다.
        if int(getattr(self, "cooker_dryer_entry_guard", 0)) > 0:
            return True

        # 진짜 cooker OFF라기엔 너무 작은/비일관적인 변화량이면 dryer mode fluctuation으로 본다.
        return (
            d_p <= COOKER_DRYER_FALSE_COOKER_OFF_PABS_MAX or
            d_i <= COOKER_DRYER_FALSE_COOKER_OFF_IRMS_MAX or
            d_h1 <= COOKER_DRYER_FALSE_COOKER_OFF_H1_MAX
        )

    def _should_block_false_cooker_off_during_three_on_dryer_mode_change(self, event, latest):
        """v34: 3개가 모두 ON일 때 드라이기 모드 변경을 COOKER_OFF로 오인하는 경로 차단.

        로그상 fast_high에서 낮은 모드로 바꿀 때 전체 파형은 여전히 dryer/cooker 동작 영역인데,
        delta classifier가 일시적으로 OFF COOKER를 골라 COOKER_OFF + FAN_ON + DRYER_ON으로 무너졌다.
        실제 cooker OFF라면 cooker heating 크기의 delta가 더 크게 빠지는 경향이 있으므로,
        3기기 ON + dryer alive 상황에서 너무 작은 cooker-off 후보는 dryer mode change로 본다.
        """
        if event is None or not latest:
            return False
        if not self._has_three_on_context():
            return False
        if not _is_dryer_alive_features(latest):
            return False
        if _is_cooker_standby_off_features(latest):
            return False

        delta = event.get("delta", {}) or {}
        d_p = abs(_safe_float(delta.get("Pabs_mean_proxy", 0.0)))
        d_i = abs(_safe_float(delta.get("Irms_adc", 0.0)))
        d_h1 = abs(_safe_float(delta.get("H1_60_mag", 0.0)))

        small_for_real_cooker_off = (
            d_p < THREE_ON_FALSE_COOKER_OFF_PABS_MAX or
            d_i < THREE_ON_FALSE_COOKER_OFF_IRMS_MAX or
            d_h1 < THREE_ON_FALSE_COOKER_OFF_H1_MAX
        )
        if small_for_real_cooker_off:
            return True

        # absolute가 dryer를 강하게 보고 있고 현재가 계속 dryer alive이면 모드 변경 가능성이 높다.
        ai_result = self.latest_ai_result or {}
        abs_device = _normalize_device_name(ai_result.get("device", None))
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0))
        if abs_device == "dryer" and abs_conf >= 0.75:
            return True

        return False

    def _should_block_cooker_on_due_to_dryer_context(self, latest):
        """v31: COOKER_OFF 위의 DRYER 재가동/모드변경을 COOKER_ON으로 오인하지 않게 막는다.

        v30의 문제:
        - DRYER_OFF 잔상/slot memory까지 dryer context로 너무 넓게 보았다.
        - 그래서 COOKER_OFF + FAN_ON + DRYER_OFF 상태에서 실제 밥솥 취사 버튼을 눌러도
          COOKER_ON을 막고, 이후 DRYER_ON으로 꼬이는 현상이 생겼다.

        v38 기준:
        - DRYER_ON이 실제 active인 동안에는 broad dryer-mode-change 차단을 유지한다.
        - DRYER_OFF 잔상만 있는 상태에서는 fast_high급 초고출력 재가동만 차단한다.
        - COOKER_OFF만 있는 상태에서도 fast_high급 초고출력은 cooker가 아니라 dryer로 본다.
        - 실제 cooker heating 영역(I≈300~400, Pabs≈160k~230k, H1≈14k~19k)은 허용한다.
        """
        if not latest:
            return False

        if not self._has_cooker_off_context():
            return False

        has_fan_on = self._has_fan_on_context()
        has_active_dryer = any(
            x.get("device") == "dryer" and x.get("state") == "on"
            for x in self.active_devices
        )
        has_dryer_memory = self._has_dryer_context()

        p = _safe_float(latest.get("Pabs_mean_proxy", 0.0))
        i = _safe_float(latest.get("Irms_adc", 0.0))
        h1 = _safe_float(latest.get("H1_60_mag", 0.0))

        # v38:
        # COOKER_OFF만 잡힌 상태에서 드라이기를 fast_high로 켜면,
        # RF absolute 모델이 cooker를 강하게 보면서 COOKER_ON으로 먼저 승격되는 문제가 있었다.
        # 실제 cooker 취사 단독은 보통 Pabs≈200k/I≈350/H1≈17k 영역이고,
        # fast_high dryer는 Pabs/I/H1이 훨씬 큰 초고출력 영역으로 튄다.
        # 따라서 cooker_off context 위에서 초고출력 dryer 영역이면 fan/dryer memory가 없어도
        # COOKER_ON을 차단하고 DRYER_ON으로 변환한다.
        if _is_fast_high_dryer_features(latest) and not _is_real_cooker_heating_with_fan_features(latest):
            return True

        if not (has_active_dryer or has_dryer_memory or has_fan_on):
            return False

        score = 0
        if p >= COOKER_FALSE_ON_DRYER_CONTEXT_PABS_MIN:
            score += 1
        if i >= COOKER_FALSE_ON_DRYER_CONTEXT_IRMS_MIN:
            score += 1
        if h1 >= COOKER_FALSE_ON_DRYER_CONTEXT_H1_MIN:
            score += 1

        fast_score = 0
        if p >= COOKER_FALSE_FAST_DRYER_PABS_MIN:
            fast_score += 1
        if i >= COOKER_FALSE_FAST_DRYER_IRMS_MIN:
            fast_score += 1
        if h1 >= COOKER_FALSE_FAST_DRYER_H1_MIN:
            fast_score += 1

        # v33: COOKER_OFF + FAN_ON 상태에서 매우 큰 dryer fast_high급 영역으로 바로 튀면
        # DRYER_OFF 잔상이 남아 있지 않더라도 실제 cooker 취사가 아니라 dryer 재가동으로 본다.
        # v32에서는 has_dryer_memory가 없으면 이 경로가 막히지 않아 COOKER_ON으로 먼저 올라갔다.
        if has_fan_on and _is_fast_high_dryer_features(latest):
            return True

        # v33: COOKER_OFF + FAN_ON 상태에서 dryer_alive 크기의 부하가 추가되었는데
        # 실제 cooker heating with fan 박스가 아니면 cooker 승격을 막는다.
        # slow_low/slow_mid dryer도 cooker가 아니라 dryer로 올라가게 하기 위한 공통 gate.
        if has_fan_on and _is_dryer_alive_features(latest) and not _is_real_cooker_heating_with_fan_features(latest):
            return True

        # DRYER가 실제 ON 상태에서 출력만 바뀌는 경우는 broad 조건으로 막는다.
        if has_active_dryer:
            return score >= 2

        # DRYER_OFF 잔상 + FAN_ON 상태에서는 두 경우를 반드시 분리해야 한다.
        # 1) 실제 cooker 취사 재시작: I/Pabs/H1이 cooker heating with fan 후보 영역에 들어옴 → 허용
        # 2) dryer 재가동/램프업: cooker처럼 보이는 broad 상승 또는 fast_high 초고출력 → COOKER_ON 차단
        # v31에서는 이 구간을 fast_high만 막아서, dryer ON 초반 램프업(I≈232, Pabs≈123k, H1≈10.6k)이
        # COOKER_ON으로 먼저 올라가는 문제가 있었다.
        if has_dryer_memory and has_fan_on:
            if _is_real_cooker_heating_with_fan_features(latest) and not _is_fast_high_dryer_features(latest):
                return False
            return score >= 2 or fast_score >= 2

        # dryer memory가 없고 fan/cooker만 있는 상태에서는 실제 cooker ON을 허용한다.
        return False


    def _should_block_false_fan_off_during_fast_dryer(self, event, latest):
        """v30: fast_high 드라이기 유지 중의 흔들림을 FAN_OFF로 오인하지 않게 막는다.

        실제 FAN_OFF라면 Pabs/I/H1이 함께 음수 방향으로 내려가는 경향이 있어야 한다.
        반대로 fast_high 드라이기 자체 흔들림은 Pabs만 음수이고 I/H1이 양수 또는 거의 0으로
        흔들릴 수 있으므로, COOKER_OFF + FAN_ON + DRYER context에서는 FAN_OFF를 취소한다.
        """
        if event is None or not latest:
            return False

        has_fan = any(x.get("device") == "fan" and x.get("state") == "on" for x in self.active_devices)
        has_dryer = any(x.get("device") == "dryer" and x.get("state") == "on" for x in self.active_devices)
        if not has_fan or not has_dryer:
            return False

        delta = event.get("delta", {}) or {}
        d_p = _safe_float(delta.get("Pabs_mean_proxy", 0.0))
        d_i = _safe_float(delta.get("Irms_adc", 0.0))
        d_h1 = _safe_float(delta.get("H1_60_mag", 0.0))

        # v37: 세 기기가 모두 ON이고 dryer가 여전히 고출력으로 살아있으면,
        # dH1이 거의 빠지지 않는 약한 FAN_OFF 후보는 dryer fluctuation으로 본다.
        if self._has_three_on_context() and _is_dryer_alive_features(latest):
            weak_fan_off_like = (
                d_p <= -ON_DELTA_PABS_MIN and
                abs(d_p) <= THREE_ON_WEAK_FAN_OFF_PABS_MAX and
                abs(d_i) <= THREE_ON_WEAK_FAN_OFF_IRMS_MAX and
                abs(d_h1) <= THREE_ON_WEAK_FAN_OFF_H1_MAX
            )
            if weak_fan_off_like:
                return True

        # v34: 3기기 ON 또는 COOKER context에서 dryer mode를 바꾸면
        # 큰 음수 delta가 FAN_OFF처럼 선택될 수 있다. 실제 fan OFF보다 훨씬 큰 변화량이면 보호한다.
        has_cooker_context = (
            any(x.get("device") == "cooker" and x.get("state") == "on" for x in self.active_devices) or
            self._has_cooker_off_context()
        )
        delta = event.get("delta", {}) or {}
        d_p = _safe_float(delta.get("Pabs_mean_proxy", 0.0))
        d_i = _safe_float(delta.get("Irms_adc", 0.0))
        d_h1 = _safe_float(delta.get("H1_60_mag", 0.0))

        if has_cooker_context and _is_dryer_alive_features(latest):
            too_large_for_real_fan_off = (
                abs(d_p) > FAN_OFF_WITH_DRYER_PABS_MAX or
                abs(d_i) > FAN_OFF_WITH_DRYER_IRMS_MAX or
                abs(d_h1) > FAN_OFF_WITH_DRYER_H1_MAX
            )
            if too_large_for_real_fan_off:
                return True

        if not self._has_cooker_off_context():
            return False

        if not _is_fast_high_dryer_features(latest):
            return False

        delta = event.get("delta", {}) or {}
        d_p = _safe_float(delta.get("Pabs_mean_proxy", 0.0))
        d_i = _safe_float(delta.get("Irms_adc", 0.0))
        d_h1 = _safe_float(delta.get("H1_60_mag", 0.0))

        # 세 축이 모두 fan OFF 방향이면 실제 선풍기 OFF일 가능성이 있으므로 막지 않는다.
        coherent_fan_off = (
            d_p <= -FAN_OFF_WITH_DRYER_PABS_MIN and
            d_i <= -FAN_OFF_WITH_DRYER_IRMS_MIN and
            d_h1 <= -FAN_OFF_WITH_DRYER_H1_MIN
        )
        if coherent_fan_off:
            return False

        # Pabs만 내려가고 I/H1이 내려가지 않으면 fast_high 드라이기 흔들림으로 본다.
        if d_p <= -ON_DELTA_PABS_MIN and (d_i > -FAN_OFF_WITH_DRYER_IRMS_MIN or d_h1 > -FAN_OFF_WITH_DRYER_H1_MIN):
            return True

        return False

    def update(self, ai_result):
        """
        NILMAIExtension의 예측 결과를 받아 active device 상태를 갱신한다.

        v3 핵심:
        - fan ON은 즉시 확정하지 않고 pending 후 확인한다.
        - fan OFF로 제거된 직후 absolute 모델이 fan을 계속 보면 복구한다.
        - plugged_off 상태의 약한 fan 이벤트는 유령 이벤트 가능성이 커서 보수적으로 처리한다.
        """
        if not ai_result or not ai_result.get("ready", False):
            return self._make_output(ai_result, event=None)

        latest = ai_result.get("block_features") or self._result_to_minimal_features(ai_result)
        self.latest_ai_result = ai_result
        self.latest_features = latest
        self.feature_history.append(latest)

        global_state = str(ai_result.get("state", "empty")).lower()

        # idle baseline은 active device가 없고, 전체 상태가 on이 아닐 때만 천천히 갱신한다.
        if not self.active_devices and global_state != "on":
            self.idle_rows.append(latest)
            if len(self.idle_rows) >= IDLE_BASELINE_BLOCKS:
                self.idle_baseline = _mean_features(list(self.idle_rows))

        self._tick_recent_off_memory()
        if self.dryer_mode_shift_guard > 0:
            self.dryer_mode_shift_guard -= 1

        event = None

        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            event = self._detect_event()

            if event is not None:
                self.cooldown = EVENT_COOLDOWN_BLOCKS
                self.last_event = event

                if event["type"] == "on":
                    self._handle_on_event(event)
                elif event["type"] == "off":
                    self._handle_off_event(event)

        # pending fan 후보 확인 및 OFF 후 복구를 매 block 수행한다.
        self._update_pending_on(ai_result, latest)
        self._recover_recent_off_if_needed(ai_result, latest)
        self._recover_dryer_if_needed(ai_result, latest)

        # v6: 이벤트 기반 tracker가 놓치거나 잘못 남긴 상태를 absolute 판단으로 보정
        self._sync_absolute_device_if_needed(ai_result, latest)
        self._prune_stale_active_devices(ai_result, latest)
        self._detect_fan_by_dryer_residual(ai_result, latest)
        self._detect_fan_off_by_dryer_residual(ai_result, latest)
        self._recover_fan_after_dryer_off(ai_result, latest)
        self._reconcile_signature_stack(ai_result, latest)
        self._update_dryer_baseline(ai_result, latest)

        if self.post_dryer_off_recovery_left > 0:
            self.post_dryer_off_recovery_left -= 1
        if int(getattr(self, "cooker_dryer_entry_guard", 0)) > 0:
            self.cooker_dryer_entry_guard -= 1

        self._tick_off_events()
        return self._make_output(ai_result, event=event)

    def _result_to_minimal_features(self, ai_result):
        """
        혹시 block_features가 없을 때를 대비한 fallback.
        """
        row = {col: 0.0 for col in BASE_FEATURE_COLS}
        row["Irms_adc"] = _safe_float(ai_result.get("Irms_adc", 0.0))
        row["Pabs_mean_proxy"] = _safe_float(ai_result.get("Pabs_mean_proxy", 0.0))
        row["H1_60_mag"] = _safe_float(ai_result.get("H1_60_mag", 0.0))
        row["THD_i"] = _safe_float(ai_result.get("THD_i", 0.0))
        row["fft_peak_freq"] = _safe_float(ai_result.get("fft_peak_freq", 0.0))
        return row

    def _detect_event(self):
        if len(self.feature_history) < (DELTA_OLD_N + DELTA_NEW_N):
            return None

        rows = list(self.feature_history)
        old_rows = rows[-(DELTA_OLD_N + DELTA_NEW_N):-DELTA_NEW_N]
        new_rows = rows[-DELTA_NEW_N:]

        old_mean = _mean_features(old_rows)
        new_mean = _mean_features(new_rows)

        delta = {}
        for col in BASE_FEATURE_COLS:
            delta[col] = _safe_float(new_mean.get(col, 0.0)) - _safe_float(old_mean.get(col, 0.0))

        direction = _event_direction(delta)
        if direction is None:
            return None

        score = _delta_score(delta)
        if score < EVENT_SCORE_MIN:
            return None

        return {
            "type": direction,
            "score": score,
            "delta": delta,
            "old_mean": old_mean,
            "new_mean": new_mean,
            "old_rows": old_rows,
            "new_rows": new_rows,
        }

    def _make_delta_rows(self, event, positive=True):
        """
        device classifier에 넣기 위한 delta window feature 생성.
        positive=True: ON 이벤트. new - old를 양수 기여분으로 사용.
        positive=False: OFF 이벤트. old - new를 양수 기여분으로 사용.
        """
        baseline = event["old_mean"] if positive else event["new_mean"]
        source_rows = event["new_rows"] if positive else event["old_rows"]

        delta_rows = []
        for row in source_rows:
            drow = {}
            for col in BASE_FEATURE_COLS:
                if positive:
                    v = _safe_float(row.get(col, 0.0)) - _safe_float(baseline.get(col, 0.0))
                else:
                    v = _safe_float(row.get(col, 0.0)) - _safe_float(baseline.get(col, 0.0))

                if col in NONNEGATIVE_FEATURES:
                    v = max(0.0, v)

                if abs(v) < DELTA_EPS:
                    v = 0.0

                drow[col] = float(v)
            delta_rows.append(drow)

        return delta_rows

    def _predict_device_from_delta(self, event, positive=True):
        """
        delta feature를 이용해 추가/제거된 기기를 추정한다.

        v2 수정 핵심:
        1. ready result에 block_features를 포함시켜 전체 feature delta를 사용한다.
        2. RF device 모델 결과만 믿지 않고, delta 크기 기반 guard를 적용한다.
           dryer처럼 큰 부하가 fan으로 오분류되는 문제를 막기 위함이다.
        """
        delta_rows = self._make_delta_rows(event, positive=positive)

        try:
            X_device = make_window_features_from_blocks(
                delta_rows,
                self.ai.device_feature_names,
            )

            raw_device, conf, probs = predict_with_proba(
                self.ai.device_model,
                X_device,
                labels_from_json=self.ai.device_labels,
            )

            raw_device = _normalize_device_name(raw_device)

            guard_device, guard_reason = _guard_device_by_delta_size(
                event,
                model_device=raw_device,
                model_conf=conf,
            )

            # v23: cooker 보정은 device 모델이 cooker를 충분히 본 경우 그대로 통과시킨다.
            if guard_device == "cooker":
                if self.verbose and raw_device != "cooker":
                    print(
                        f"[DELTA DEVICE GUARD] {str(raw_device).upper()} -> COOKER | "
                        f"reason={guard_reason} | model_conf={conf:.2f} | "
                        f"probs[{format_prob_dict(probs, topk=4)}]"
                    )
                return "cooker", max(float(conf), COOKER_DELTA_MIN_CONF), probs

            # dryer 강제 보정은 confidence와 무관하게 우선한다.
            if guard_device == "dryer":
                if self.verbose and raw_device != "dryer":
                    print(
                        f"[DELTA DEVICE GUARD] {str(raw_device).upper()} -> DRYER | "
                        f"reason={guard_reason} | model_conf={conf:.2f} | "
                        f"probs[{format_prob_dict(probs, topk=4)}]"
                    )
                return "dryer", max(float(conf), 0.90), probs

            # fan은 작은 부하 영역일 때만 fan으로 인정한다.
            if raw_device == "fan":
                if guard_device == "fan":
                    return "fan", float(conf), probs

                # fan이라고 나왔지만 변화량이 fan 범위를 벗어나면 unknown 처리.
                # 이렇게 해야 dryer 큰 부하를 fan으로 잘못 active list에 넣는 걸 막을 수 있다.
                if self.verbose:
                    sig = _event_signature_magnitude(event)
                    print(
                        "[DELTA DEVICE GUARD] FAN rejected by size | "
                        f"Pabs={sig['Pabs_mean_proxy']:.1f}, "
                        f"I={sig['Irms_adc']:.2f}, "
                        f"H1={sig['H1_60_mag']:.1f} | "
                        f"model_conf={conf:.2f} | "
                        f"probs[{format_prob_dict(probs, topk=4)}]"
                    )
                return None, float(conf), probs

            # v10: charger는 active를 막는 대신, 후보 단계에서 확률 우세/feature plausibility를 검증한다.
            if raw_device == "charger":
                ok, reason = _charger_delta_candidate_is_reliable(event, probs, conf)
                if not ok:
                    if self.verbose:
                        sig = _event_signature_magnitude(event)
                        print(
                            "[DELTA DEVICE GUARD] CHARGER candidate rejected | "
                            f"reason={reason} | "
                            f"Pabs={sig['Pabs_mean_proxy']:.1f}, "
                            f"I={sig['Irms_adc']:.2f}, "
                            f"H1={sig['H1_60_mag']:.1f} | "
                            f"model_conf={conf:.2f} | "
                            f"probs[{format_prob_dict(probs, topk=4)}]"
                        )
                    return None, float(conf), probs
                if self.verbose:
                    print(f"[DELTA DEVICE GUARD] CHARGER candidate accepted | reason={reason}")
                return "charger", float(max(conf, CHARGER_ACTIVE_MIN_CONF)), probs

            device = raw_device
            if conf < DELTA_DEVICE_MIN_CONF:
                device = None

            return device, float(conf), probs

        except Exception as e:
            if self.verbose:
                print(f"[DELTA DEVICE ERROR] {e}")
            return None, 0.0, {}


    def _handle_on_event(self, event):
        device, conf, probs = self._predict_device_from_delta(event, positive=True)

        if device is None:
            if self.verbose:
                print(
                    "[DELTA EVENT] ON detected but device unknown | "
                    f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                    f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                    f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                )
            return

        ai_result = self.latest_ai_result or {}
        state = str(ai_result.get("state", "empty")).lower()
        state_probs = ai_result.get("state_probs", {}) or {}
        on_prob = _safe_float(state_probs.get("on", 0.0))
        latest = self.latest_features or {}
        abs_device = _normalize_device_name(ai_result.get("device", None))
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0))
        device_probs = ai_result.get("device_probs", {}) or {}
        cooker_prob = _prob_for(device_probs, "cooker")
        fan_prob = _prob_for(device_probs, "fan")

        # v28: COOKER_OFF + FAN_ON/DRYER context에서 드라이기 재가동 또는 출력 변경이
        # cooker heating처럼 크게 보이더라도, 이것을 COOKER_ON으로 승격하지 않는다.
        # DRYER는 이후 recovery/absolute sync 경로에서 같은 slot으로 복구/유지된다.
        if device == "cooker" and self._should_block_cooker_on_due_to_dryer_context(latest):
            self.cooker_abs_sync_hits = 0
            dryer_prob_for_block = _prob_for(ai_result.get('device_probs', {}) or {}, 'dryer')
            if self.verbose:
                print(
                    "[DELTA SELECT] ON COOKER blocked: dryer mode/restart over COOKER_OFF suspected | "
                    f"abs_device={abs_device}, abs_conf={abs_conf:.2f}, cooker_prob={cooker_prob:.2f}, "
                    f"dryer_prob={dryer_prob_for_block:.2f}, "
                    f"I={_safe_float(latest.get('Irms_adc', 0.0)):.2f}, "
                    f"Pabs={_safe_float(latest.get('Pabs_mean_proxy', 0.0)):.1f}, "
                    f"H1={_safe_float(latest.get('H1_60_mag', 0.0)):.1f}"
                )

            # v33: cooker 승격을 막는 데서 끝내면 화면이 COOKER_OFF+FAN_ON에 머물렀다.
            # 현재 feature가 dryer_alive이고 실제 cooker heating 박스가 아니면, 이 ON 이벤트는
            # dryer 재가동/모드 상승으로 처리해서 DRYER_ON을 같은 흐름에서 올린다.
            if _is_dryer_alive_features(latest) and not _is_real_cooker_heating_with_fan_features(latest):
                self._add_active_device(
                    "dryer",
                    max(dryer_prob_for_block, abs_conf, conf, 0.80),
                    ai_result.get("device_probs", {}) or {},
                    event=event,
                    source="blocked_cooker_as_dryer_v33",
                )
            return

        # v24: cooker 플러그만 꽂은 대기/취사 OFF profile은 COOKER_ON이 아니라 COOKER_OFF로 표시한다.
        # 플러그 삽입 순간 일시적인 spike도 state/on_prob가 안정되기 전에는 ON으로 올리지 않는다.
        if device == "cooker":
            if _is_cooker_standby_off_features(latest):
                self._mark_device_off("cooker", conf=max(conf, abs_conf), source="cooker_standby_off")
                if self.verbose:
                    print(
                        "[DELTA EVENT] ON COOKER converted to COOKER_OFF: standby/off profile | "
                        f"state={state}, on_prob={on_prob:.2f}, "
                        f"I={_safe_float(latest.get('Irms_adc', 0.0)):.2f}, "
                        f"Pabs={_safe_float(latest.get('Pabs_mean_proxy', 0.0)):.1f}, "
                        f"H1={_safe_float(latest.get('H1_60_mag', 0.0)):.1f}"
                    )
                return

            if COOKER_ON_REQUIRE_STATE_ON and (state != "on" or on_prob < COOKER_ON_REQUIRE_ON_PROB):
                self._mark_device_off("cooker", conf=max(conf, abs_conf), source="cooker_on_deferred_unstable_state")
                if self.verbose:
                    print(
                        "[DELTA EVENT] ON COOKER deferred/marked OFF: waiting stable cooker heating | "
                        f"state={state}, on_prob={on_prob:.2f}, "
                        f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                        f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                        f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                    )
                return

        # v24: cooker OFF/standby가 이미 잡힌 상태에서 취사 버튼을 누르면 delta가 dryer급으로 커져
        # device 모델이 dryer로 예측할 수 있다. 하지만 absolute 모델이 cooker를 지지하고 현재 feature가
        # cooker heating이면 DRYER_ON이 아니라 기존 cooker slot을 COOKER_ON으로 전환한다.
        cooker_known = (
            any(x.get("device") == "cooker" for x in self.active_devices) or
            any(x.get("device") == "cooker" for x in self.off_events) or
            any(info.get("device") == "cooker" for info in self.retained_off_slots.values())
        )
        dryer_active_now_for_cooker = any(x.get("device") == "dryer" for x in self.active_devices)
        if (
            device == "dryer" and
            cooker_known and
            not dryer_active_now_for_cooker and
            _is_cooker_heating_features(latest) and
            (abs_device == "cooker" or cooker_prob >= 0.25)
        ):
            if self.verbose:
                print(
                    "[DELTA SELECT] ON DRYER -> COOKER: cooker heating transition suspected | "
                    f"abs_device={abs_device}, abs_conf={abs_conf:.2f}, cooker_prob={cooker_prob:.2f}, "
                    f"I={_safe_float(latest.get('Irms_adc', 0.0)):.2f}, "
                    f"Pabs={_safe_float(latest.get('Pabs_mean_proxy', 0.0)):.1f}, "
                    f"H1={_safe_float(latest.get('H1_60_mag', 0.0)):.1f}"
                )
            device = "cooker"
            conf = max(conf, abs_conf, cooker_prob, 0.80)

        # v6: dryer 플러그 삽입/접점 순간 스파이크가 dryer ON으로 바로 표시되는 문제 방지.
        # 실제로 켠 경우에는 몇 block 뒤 absolute model이 dryer/on을 안정적으로 보므로
        # _sync_absolute_device_if_needed()에서 DRYER_ON으로 올린다.
        if device == "dryer" and DEFER_DRYER_UNTIL_STABLE_ON and (state != "on" or on_prob < DRYER_ON_REQUIRE_ON_PROB):
            # 플러그 삽입/접점 스파이크가 dryer delta로 보이는 경우가 많다.
            # state/on_prob가 안정되기 전에는 active stack에 올리지 않고 absolute sync에 맡긴다.
            if self.verbose:
                print(
                    f"[DELTA EVENT] ON DRYER deferred: waiting stable ON state={state}, on_prob={on_prob:.2f} | "
                    f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                    f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                    f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                )
            return

        # v3: plugged_off 상태에서 발생한 약한 fan ON은 바로 확정하지 않는다.
        # dryer급 큰 이벤트는 state 모델이 늦게 따라오는 경우가 많아서 허용한다.
        if BLOCK_WEAK_ON_WHEN_NOT_ON and state != "on" and on_prob < FAN_ON_MIN_ON_PROB:
            if not _is_dryer_sized_event(event):
                if self.verbose:
                    print(
                        f"[DELTA EVENT] ON {device.upper()} ignored: weak event while state={state}, "
                        f"on_prob={on_prob:.2f} | "
                        f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                        f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                        f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                    )
                return

        # v5: fan은 즉시 active에 넣지 않고 pending 후 확인한다.
        # 단, active dryer가 없는 상태에서 new_mean 자체가 dryer급이면
        # 드라이기 램프업/출력변화가 fan-sized delta처럼 보인 것이므로 fan 후보를 만들지 않는다.
        if device == "fan":
            dryer_active_now = any(x.get("device") == "dryer" for x in self.active_devices)

            # v7: dryer가 active인 동안 생기는 fan 후보는 대부분 dryer 출력 변동이다.
            # 따라서 standalone fan 범위보다 더 엄격한 fan-with-dryer 범위를 통과해야 한다.
            if dryer_active_now and not _is_fan_sized_with_dryer_event(event, conf):
                # v15: 고출력 dryer에서는 Pabs가 흔들려도 I/H1 축이 fan-like이면 후보를 버리지 않는다.
                if _is_high_dryer_fan_axis_event(event, conf):
                    self.high_dryer_fan_axis_hits = int(getattr(self, "high_dryer_fan_axis_hits", 0)) + 1
                    if self.dryer_baseline is not None and self.dryer_baseline_frozen is None:
                        self.dryer_baseline_frozen = dict(self.dryer_baseline)
                    self.dryer_baseline_freeze_left = max(self.dryer_baseline_freeze_left, DRYER_BASELINE_FREEZE_BLOCKS)
                    if self.high_dryer_fan_axis_hits < HIGH_DRYER_FAN_HITS_REQUIRED:
                        if self.verbose:
                            print(
                                "[DELTA EVENT] ON FAN high-dryer axis pending | "
                                f"hits={self.high_dryer_fan_axis_hits}/{HIGH_DRYER_FAN_HITS_REQUIRED}, "
                                f"conf={conf:.2f}, "
                                f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                                f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                                f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                            )
                        return
                    self.high_dryer_fan_axis_hits = 0
                    self._add_active_device("fan", max(conf, 0.84), probs, event, source="high_dryer_axis")
                    if self.verbose:
                        print(
                            "[DELTA EVENT] ON FAN slot confirmed by high-dryer axis | "
                            f"conf={conf:.2f}, "
                            f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                            f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                            f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                        )
                    return
                else:
                    self.high_dryer_fan_axis_hits = max(0, int(getattr(self, "high_dryer_fan_axis_hits", 0)) - 1)
                    if self.verbose:
                        print(
                            "[DELTA EVENT] FAN ON ignored: dryer fluctuation suspected(v15 strict) | "
                            f"conf={conf:.2f}, "
                            f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                            f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                            f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                        )
                    return

            if not _is_fan_sized_event(event):
                # v26: COOKER_OFF 위에 fan을 켜면 delta I가 5~7 정도로 작게 잡혀
                # 기존 fan-sized 조건(I>=8)을 통과하지 못한다. 대신 현재 absolute feature가
                # cooker_off+fan profile이면 FAN_ON으로 확정한다.
                if self._has_cooker_off_context() and _is_cooker_plus_fan_features(latest):
                    self.cooker_fan_abs_hits = int(getattr(self, "cooker_fan_abs_hits", 0)) + 1
                    if self.cooker_fan_abs_hits >= COOKER_PLUS_FAN_HITS_REQUIRED:
                        self._add_active_device(
                            "fan",
                            max(conf, fan_prob, 0.80),
                            probs,
                            event,
                            source="cooker_off_fan_delta",
                        )
                        self.cooker_fan_abs_hits = 0
                    else:
                        if self.verbose:
                            print(
                                "[DELTA EVENT] FAN over COOKER_OFF pending | "
                                f"hits={self.cooker_fan_abs_hits}/{COOKER_PLUS_FAN_HITS_REQUIRED}, "
                                f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                                f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                                f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                            )
                    return

                if self.verbose:
                    print(
                        "[DELTA EVENT] FAN ON ignored: not fan-sized delta | "
                        f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                        f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                        f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                    )
                return

            if (not dryer_active_now) and _event_new_mean_is_dryer_alive(event):
                if self.verbose:
                    print(
                        "[DELTA EVENT] FAN ON ignored: dryer ramp suspected before dryer tracking | "
                        f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                        f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                        f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                    )
                return

            self._start_pending_on(device, conf, probs, event)
            return

        self._add_active_device(device, conf, probs, event, source="delta")

    def _mark_device_off(self, device, conf=0.80, source="manual_off_detected"):
        """active에 올리지 않고 특정 기기를 *_OFF 상태로 표시/기억한다.

        cooker처럼 플러그만 꽂아도 낮은 전류가 보이는 기기는 active ON이 아니라
        COOKER_OFF로 보여야 하므로 이 경로를 사용한다.
        """
        device = _normalize_device_name(device)
        if device is None:
            return False

        # 같은 device의 ON이 있으면 제거하고 같은 slot을 재사용한다.
        existing_slots = []
        kept = []
        for item in self.active_devices:
            if item.get("device") == device:
                existing_slots.append(int(item.get("slot", 0)))
            else:
                kept.append(item)
        self.active_devices = kept

        slot = existing_slots[0] if existing_slots else self._slot_for_device(device)
        if USE_DEVICE_SLOT_MEMORY:
            self.device_slot_memory[device] = slot

        self.off_events = deque(
            [x for x in self.off_events if x.get("device") != device],
            maxlen=MAX_ACTIVE_DEVICES,
        )
        self.off_events.append({
            "device": device,
            "slot": slot,
            "hold": OFF_HOLD_BLOCKS,
            "conf": max(_safe_float(conf, 0.0), 0.80),
            "source": source,
        })
        self.recent_off_devices[device] = RECENT_OFF_MEMORY_BLOCKS
        self.recovery_hits[device] = 0
        self._remember_retained_off({"device": device, "slot": slot, "conf": conf, "source": source})

        if self.verbose:
            print(f"[DELTA EVENT] {device.upper()} marked OFF source={source} slot={slot + 1}")
        return True

    def _add_active_device(self, device, conf, probs, event=None, source="delta"):
        """active_devices에 기기를 추가하거나 이미 있으면 갱신한다."""
        device = _normalize_device_name(device)
        if device is None:
            return False

        # v29: COOKER_OFF + FAN_ON/DRYER context에서 dryer fast_high/모드 변경이
        # cooker로 들어오면 active에 추가되기 전에 차단한다.
        # v28의 _handle_on_event / absolute sync 차단을 우회하는 delta 경로까지 막기 위한 최종 방어막이다.
        if device == "cooker" and self._should_block_cooker_on_due_to_dryer_context(self.latest_features or {}):
            self.cooker_abs_sync_hits = 0
            latest = self.latest_features or {}
            self._mark_device_off("cooker", conf=max(_safe_float(conf, 0.0), 0.80), source="blocked_false_cooker_fast_dryer")
            if self.verbose:
                print(
                    "[DELTA EVENT] ON COOKER blocked before active: dryer fast_high/mode context | "
                    f"source={source}, conf={_safe_float(conf, 0.0):.2f}, "
                    f"I={_safe_float(latest.get('Irms_adc', 0.0)):.2f}, "
                    f"Pabs={_safe_float(latest.get('Pabs_mean_proxy', 0.0)):.1f}, "
                    f"H1={_safe_float(latest.get('H1_60_mag', 0.0)):.1f}"
                )
            # v33: 이 cooker add가 dryer 재가동으로 차단된 경우에는 DRYER_ON으로 변환한다.
            if _is_dryer_alive_features(latest) and not _is_real_cooker_heating_with_fan_features(latest):
                # 직접 append하면 중복/slot 문제가 생기므로, cooker 방어막을 벗어난 dryer add로 재호출한다.
                return self._add_active_device(
                    "dryer",
                    max(_safe_float(conf, 0.0), 0.80),
                    probs,
                    event=event,
                    source="blocked_cooker_as_dryer_v33",
                )
            return False

        # v10: charger active 자체는 허용한다. 다만 최저 confidence 미만이면 active에 넣지 않는다.
        # 후보의 애매함은 _predict_device_from_delta / _sync_absolute_device_if_needed에서 먼저 제거한다.
        if device == "charger" and _should_block_charger_active(conf):
            if self.verbose:
                print(f"[DELTA EVENT] ON CHARGER ignored: low charger confidence | conf={_safe_float(conf, 0.0):.2f}")
            return False

        # v5: dryer가 새로 확정되는 순간, dryer 추적 전에 만들어진 fan pending은
        # 드라이기 램프업을 fan으로 오해한 후보일 가능성이 크므로 폐기한다.
        if device == "dryer" and self.pending_on and self.pending_on.get("device") == "fan":
            if not self.pending_on.get("dryer_active_at_start", False):
                if self.verbose:
                    print("[DELTA EVENT] ON FAN pending canceled: dryer ON confirmed")
                self.pending_on = None

        if not ALLOW_DUPLICATE_SAME_DEVICE:
            for item in self.active_devices:
                if item["device"] == device:
                    item["state"] = "on"
                    item["hold"] = 0
                    if event is not None:
                        item["signature"] = self._signature_from_event(event)
                    item["conf"] = conf
                    item["probs"] = probs
                    self._clear_retained_off(device=device, slot=int(item.get("slot", 0)))
                    self.off_events = deque(
                        [x for x in self.off_events if x.get("device") != device],
                        maxlen=MAX_ACTIVE_DEVICES,
                    )
                    self.recent_off_devices.pop(device, None)
                    self.recovery_hits.pop(device, None)
                    if device == "dryer" and any(x.get("device") == "cooker" and x.get("state") == "on" for x in self.active_devices):
                        self.cooker_dryer_entry_guard = max(
                            int(getattr(self, "cooker_dryer_entry_guard", 0)),
                            COOKER_DRYER_ENTRY_GUARD_BLOCKS,
                        )
                    if self.verbose:
                        print(f"[DELTA EVENT] ON update {device.upper()} conf={conf:.2f} source={source}")
                    return True

        if len(self.active_devices) >= MAX_ACTIVE_DEVICES:
            if self.verbose:
                print(f"[DELTA EVENT] ON {device.upper()} ignored: active list full")
            return False

        slot = self._slot_for_device(device)
        self.active_devices.append({
            "device": device,
            "slot": slot,
            "state": "on",
            "hold": 0,
            "conf": conf,
            "signature": self._signature_from_event(event) if event is not None else self._signature_from_latest(self.latest_features),
            "probs": probs,
            "source": source,
            "age": 0,
        })

        if device == "dryer" and any(x.get("device") == "cooker" and x.get("state") == "on" for x in self.active_devices):
            self.cooker_dryer_entry_guard = max(
                int(getattr(self, "cooker_dryer_entry_guard", 0)),
                COOKER_DRYER_ENTRY_GUARD_BLOCKS,
            )

        if USE_DEVICE_SLOT_MEMORY:
            self.device_slot_memory[device] = slot

        # 같은 기기가 다시 ON 되면, 해당 slot의 지속 OFF 표시를 지운다.
        self._clear_retained_off(device=device, slot=slot)

        # 같은 기기의 OFF 잔상이 남아 있으면 제거
        self.off_events = deque(
            [x for x in self.off_events if x.get("device") != device],
            maxlen=MAX_ACTIVE_DEVICES,
        )
        self.recent_off_devices.pop(device, None)
        self.recovery_hits.pop(device, None)

        if self.verbose:
            if event is not None:
                print(
                    f"[DELTA EVENT] ON {device.upper()} slot={slot + 1} conf={conf:.2f} source={source} | "
                    f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                    f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                    f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f} | "
                    f"device_probs[{format_prob_dict(probs, topk=4)}]"
                )
            else:
                print(f"[DELTA EVENT] ON {device.upper()} slot={slot + 1} conf={conf:.2f} source={source}")
        return True

    def _start_pending_on(self, device, conf, probs, event):
        """fan ON 후보를 pending 상태로 저장한다."""
        dryer_active_at_start = any(x.get("device") == "dryer" for x in self.active_devices)
        self.pending_on = {
            "device": device,
            "conf": float(conf),
            "probs": probs,
            "event": event,
            "ttl": FAN_PENDING_TTL_BLOCKS,
            "hits": 0,
            "dryer_active_at_start": dryer_active_at_start,
            "old_mean_dryer_alive_at_start": _event_old_mean_is_dryer_alive(event),
            "new_mean_dryer_alive_at_start": _event_new_mean_is_dryer_alive(event),
        }

        if self.verbose:
            print(
                f"[DELTA EVENT] ON {device.upper()} pending | conf={conf:.2f} | "
                f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f} | "
                f"device_probs[{format_prob_dict(probs, topk=4)}]"
            )

    def _update_pending_on(self, ai_result, latest):
        """pending fan ON 후보를 후속 block으로 확인한다."""
        if not self.pending_on:
            return

        item = self.pending_on
        device = item.get("device")
        item["ttl"] = int(item.get("ttl", 0)) - 1

        if any(x.get("device") == device for x in self.active_devices):
            self.pending_on = None
            return

        state = str(ai_result.get("state", "empty")).lower() if ai_result else "empty"
        state_probs = ai_result.get("state_probs", {}) if ai_result else {}
        on_prob = _safe_float(state_probs.get("on", 0.0))
        abs_device = _normalize_device_name(ai_result.get("device", None)) if ai_result else None
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0)) if ai_result else 0.0

        confirmed = False

        if device == "fan":
            # 단독 fan: absolute 모델도 fan이라고 보고, 현재 feature가 fan 범위여야 확정.
            if (
                state == "on" and
                on_prob >= FAN_RECOVERY_MIN_ON_PROB and
                abs_device == "fan" and
                abs_conf >= FAN_ON_MIN_ABS_CONF and
                _is_fan_alive_features(latest)
            ):
                confirmed = True

            # dryer가 이미 켜져 있는 상태에서 fan이 추가되는 경우 absolute 모델은 dryer로 남을 수 있다.
            # v5: 이 경로는 pending이 만들어질 당시부터 dryer가 active였거나,
            # 최소한 old_mean이 dryer급이었던 경우에만 허용한다.
            # 그래야 드라이기 램프업 중 생긴 fan pending이, 뒤늦게 dryer가 확정된 뒤 FAN_ON으로 승격되지 않는다.
            dryer_active = any(x.get("device") == "dryer" for x in self.active_devices)
            pending_started_on_dryer = bool(item.get("dryer_active_at_start", False) or item.get("old_mean_dryer_alive_at_start", False))

            if not confirmed and dryer_active:
                if not pending_started_on_dryer:
                    # dryer 추적 전에 생긴 fan 후보는 dryer 램프업 가능성이 높으므로 폐기한다.
                    if self.verbose:
                        print("[DELTA EVENT] ON FAN pending canceled: created before dryer was stable")
                    self.pending_on = None
                    return

                # v18: 사용자가 DRYER_ON 상태에서 FAN을 다시 켜는 경우,
                # absolute model은 dryer만 강하게 보더라도 delta event 자체는 fan-sized로 잡힌다.
                # 따라서 fan-sized delta를 먼저 인정하고, 그 외의 애매한 pending만 dryer dominant로 취소한다.
                fan_delta_ok = (
                    state == "on" and
                    _is_dryer_alive_features(latest) and
                    (
                        _is_fan_sized_with_dryer_event(item.get("event"), _safe_float(item.get("conf", 0.0))) or
                        _is_high_dryer_fan_axis_event(item.get("event"), _safe_float(item.get("conf", 0.0)))
                    )
                )

                if fan_delta_ok and ALLOW_FAN_REON_BY_DELTA_WHILE_DRYER_DOMINANT:
                    confirmed = True
                else:
                    # absolute가 dryer를 우세하게 보고 있으면 fan 후보는 dryer 출력 변동일 가능성이 크다.
                    dev_probs = ai_result.get("device_probs", {}) if ai_result else {}
                    fan_prob = _safe_float(dev_probs.get("fan", 0.0))
                    if abs_device == "dryer" and abs_conf >= DRYER_DOMINANT_CANCEL_CONF and fan_prob <= DRYER_DOMINANT_CANCEL_FAN_PROB_MAX:
                        if self.verbose:
                            print(
                                f"[DELTA EVENT] ON FAN pending canceled: absolute dryer dominant(v7) "
                                f"abs_conf={abs_conf:.2f}, fan_prob={fan_prob:.2f}"
                            )
                        self.pending_on = None
                        return

        if confirmed:
            item["hits"] = int(item.get("hits", 0)) + 1
        else:
            # 한 번 삐끗했다고 바로 버리지는 않되, hit를 서서히 낮춘다.
            item["hits"] = max(0, int(item.get("hits", 0)) - 1)

        required_hits = FAN_PENDING_CONFIRM_HITS
        if device == "fan" and any(x.get("device") == "dryer" for x in self.active_devices):
            required_hits = FAN_WITH_DRYER_REQUIRED_HITS

        if item["hits"] >= required_hits:
            self._add_active_device(
                device,
                _safe_float(item.get("conf", 0.0)),
                item.get("probs", {}),
                item.get("event"),
                source="pending_confirm",
            )
            self.pending_on = None
            return

        if item["ttl"] <= 0:
            if self.verbose:
                print(f"[DELTA EVENT] ON {str(device).upper()} pending expired")
            self.pending_on = None

    def _handle_off_event(self, event):
        if not self.active_devices:
            return

        device, conf, probs = self._predict_device_from_delta(event, positive=False)
        device = self._select_off_device(device, event)

        if device is None:
            return

        latest = self.latest_features or {}
        ai_result = self.latest_ai_result or {}

        # v35: 2기기(COOKER+DRYER) 상태에서도 dryer mode fluctuation을 COOKER_OFF로 오인하지 않게 보호.
        if device == "cooker" and self._should_block_false_cooker_off_during_cooker_dryer_mode_change(event, latest):
            self._update_active_signature_from_latest("dryer", latest, conf)
            self.dryer_mode_shift_guard = max(self.dryer_mode_shift_guard, DRYER_MODE_SHIFT_GUARD_BLOCKS)
            if self.verbose:
                print(
                    "[DELTA EVENT] OFF COOKER canceled: cooker+dryer mode change protected | "
                    f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                    f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                    f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                )
            return

        # v34: 3기기 ON 상태에서 드라이기 모드 변경을 COOKER_OFF로 오인하는 경우 방지.
        if device == "cooker" and self._should_block_false_cooker_off_during_three_on_dryer_mode_change(event, latest):
            self._update_active_signature_from_latest("dryer", latest, conf)
            self.dryer_mode_shift_guard = max(self.dryer_mode_shift_guard, DRYER_MODE_SHIFT_GUARD_BLOCKS)
            if self.verbose:
                print(
                    "[DELTA EVENT] OFF COOKER canceled: three-device dryer mode change protected | "
                    f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                    f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                    f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                )
            return

        # v30: fast_high 드라이기 유지 중 Pabs 흔들림을 FAN_OFF로 오인하는 경우 방지.
        if device == "fan" and self._should_block_false_fan_off_during_fast_dryer(event, latest):
            if self.verbose:
                print(
                    "[DELTA EVENT] OFF FAN canceled: fast_high dryer fluctuation protected | "
                    f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                    f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                    f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                )
            return

        # v3: fan OFF는 쉽게 제거하지 않는다.
        # 현재 absolute feature가 여전히 fan 범위이고, 모델도 fan/on을 보고 있으면 OFF를 취소한다.
        if device == "fan" and self._should_cancel_fan_off(ai_result, latest):
            if self.verbose:
                print(
                    "[DELTA EVENT] OFF FAN canceled: fan still alive | "
                    f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                    f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                    f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                )
            return

        # v4: dryer OFF 후보가 나와도 현재 신호가 여전히 dryer급이면 OFF가 아니라 강/약 모드 전환이다.
        if device == "dryer" and self._should_cancel_dryer_off(ai_result, latest):
            self._update_active_signature_from_latest("dryer", latest, conf)
            self.dryer_mode_shift_guard = max(self.dryer_mode_shift_guard, DRYER_MODE_SHIFT_GUARD_BLOCKS)
            if self.verbose:
                print(
                    "[DELTA EVENT] OFF DRYER canceled: dryer mode change/still alive | "
                    f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                    f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                    f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                )
            return

        # v23: cooker OFF 후보가 나와도 현재 신호가 cooker급이면 OFF가 아니라 상태 변화/가열 유지로 본다.
        if device == "cooker" and self._should_cancel_cooker_off(ai_result, latest):
            self._update_active_signature_from_latest("cooker", latest, conf)
            if self.verbose:
                print(
                    "[DELTA EVENT] OFF COOKER canceled: cooker still alive | "
                    f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                    f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                    f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f}"
                )
            return

        removed = None
        remain = []
        for item in self.active_devices:
            if removed is None and item["device"] == device:
                removed = item
            else:
                remain.append(item)
        self.active_devices = remain

        if removed is not None:
            if USE_DEVICE_SLOT_MEMORY:
                self.device_slot_memory[removed["device"]] = removed["slot"]
            off_item = {
                "device": removed["device"],
                "slot": removed["slot"],
                "hold": OFF_HOLD_BLOCKS,
                "conf": conf,
            }
            self.off_events.append(off_item)
            self.recent_off_devices[removed["device"]] = RECENT_OFF_MEMORY_BLOCKS
            self.recovery_hits[removed["device"]] = 0
            if removed["device"] == "dryer":
                # v8: 드라이기 OFF 직후 fan만 남는 경우를 absolute feature로 복구할 수 있게 짧은 창을 연다.
                self.post_dryer_off_recovery_left = POST_DRYER_OFF_FAN_RECOVERY_BLOCKS
                self.post_dryer_off_fan_hits = 0
                self.fan_residual_hits = 0

            if self.verbose:
                print(
                    f"[DELTA EVENT] OFF {removed['device'].upper()} slot={removed['slot'] + 1} conf={conf:.2f} | "
                    f"dPabs={event['delta'].get('Pabs_mean_proxy', 0.0):.1f}, "
                    f"dI={event['delta'].get('Irms_adc', 0.0):.2f}, "
                    f"dH1={event['delta'].get('H1_60_mag', 0.0):.1f} | "
                    f"device_probs[{format_prob_dict(probs, topk=4)}]"
                )

    def _should_cancel_dryer_off(self, ai_result, latest):
        """OFF DRYER 후보가 나왔지만 드라이기가 약풍/저출력으로 계속 살아 있으면 제거 취소."""
        if not _is_dryer_alive_features(latest):
            return False

        state = str(ai_result.get("state", "empty")).lower() if ai_result else "empty"
        state_probs = ai_result.get("state_probs", {}) if ai_result else {}
        on_prob = _safe_float(state_probs.get("on", 0.0))
        abs_device = _normalize_device_name(ai_result.get("device", None)) if ai_result else None
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0)) if ai_result else 0.0

        # state/device가 dryer/on을 보고 있거나, feature 자체가 dryer급이면 모드 전환으로 본다.
        if state == "on" and abs_device == "dryer" and abs_conf >= 0.45:
            return True
        if on_prob >= 0.50 and abs_device == "dryer" and abs_conf >= 0.45:
            return True
        if state == "on" and _is_dryer_alive_features(latest):
            return True

        return False

    def _should_cancel_cooker_off(self, ai_result, latest):
        """OFF COOKER 후보가 나왔지만 밥솥 취사/가열이 계속 살아 있으면 제거 취소.

        v24: 낮은 cooker standby/off profile은 COOKER_ON 유지 사유가 아니다.
        즉, 취사 버튼을 껐거나 플러그만 꽂힌 상태로 내려오면 COOKER_OFF가 되어야 한다.
        """
        if not _is_cooker_alive_features(latest):
            return False

        if _is_cooker_standby_off_features(latest):
            return False

        # cooker heating profile이 아니면 ON 유지로 보지 않는다.
        if not _is_cooker_heating_features(latest):
            return False

        state = str(ai_result.get("state", "empty")).lower() if ai_result else "empty"
        state_probs = ai_result.get("state_probs", {}) if ai_result else {}
        on_prob = _safe_float(state_probs.get("on", 0.0))
        abs_device = _normalize_device_name(ai_result.get("device", None)) if ai_result else None
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0)) if ai_result else 0.0

        if state == "on" and abs_device == "cooker" and abs_conf >= COOKER_OFF_CANCEL_MIN_CONF:
            return True
        if on_prob >= COOKER_ABS_SYNC_MIN_ON_PROB and abs_device == "cooker" and abs_conf >= COOKER_OFF_CANCEL_MIN_CONF:
            return True

        return False

    def _update_active_signature_from_latest(self, device, latest, conf=0.0):
        """모드 전환으로 판단된 경우 active device의 signature를 현재 크기로 갱신한다."""
        for item in self.active_devices:
            if item.get("device") == device:
                item["state"] = "on"
                item["hold"] = 0
                item["conf"] = max(_safe_float(item.get("conf", 0.0)), _safe_float(conf, 0.0))
                item["signature"] = {
                    "Pabs_mean_proxy": _safe_float(latest.get("Pabs_mean_proxy", 0.0)),
                    "Irms_adc": _safe_float(latest.get("Irms_adc", 0.0)),
                    "H1_60_mag": _safe_float(latest.get("H1_60_mag", 0.0)),
                    "THD_i": _safe_float(latest.get("THD_i", 0.0)),
                }
                return True
        return False

    def _should_cancel_fan_off(self, ai_result, latest):
        """OFF FAN 후보가 나왔지만 fan이 여전히 살아 있는 것으로 보이면 제거 취소."""
        if not _is_fan_alive_features(latest):
            return False

        state = str(ai_result.get("state", "empty")).lower() if ai_result else "empty"
        state_probs = ai_result.get("state_probs", {}) if ai_result else {}
        on_prob = _safe_float(state_probs.get("on", 0.0))
        abs_device = _normalize_device_name(ai_result.get("device", None)) if ai_result else None
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0)) if ai_result else 0.0
        device_probs = ai_result.get("device_probs", {}) if ai_result else {}
        cooker_prob = _prob_for(device_probs, "cooker")
        fan_prob = _prob_for(device_probs, "fan")

        # v26: cooker_off 대기파형은 fan_alive 범위와 겹친다.
        # COOKER_OFF context에서는 current feature가 cooker_off+fan profile일 때만 FAN_OFF를 취소하고,
        # cooker_off 단독 profile으로 내려오면 FAN_OFF를 허용한다.
        if self._has_cooker_off_context() and not any(x.get("device") == "cooker" and x.get("state") == "on" for x in self.active_devices):
            return _is_cooker_plus_fan_features(latest)

        # v9: post-dryer-off 구간에서는 absolute device가 아직 dryer로 흔들려도
        # 현재 feature가 fan 단독 범위면 FAN_OFF를 취소한다.
        if on_prob >= 0.70:
            return True
        if self.post_dryer_off_recovery_left > 0 and on_prob >= 0.45:
            return True
        if state == "on" and abs_device == "fan" and abs_conf >= 0.65:
            return True
        if on_prob >= 0.60 and abs_device == "fan" and abs_conf >= 0.65:
            return True

        return False

    def _tick_recent_off_memory(self):
        """OFF 직후 복구 판단용 memory TTL 감소."""
        remove = []
        for dev, ttl in list(self.recent_off_devices.items()):
            ttl = int(ttl) - 1
            if ttl <= 0:
                remove.append(dev)
            else:
                self.recent_off_devices[dev] = ttl

        for dev in remove:
            self.recent_off_devices.pop(dev, None)
            self.recovery_hits.pop(dev, None)

    def _recover_recent_off_if_needed(self, ai_result, latest):
        """잘못 OFF된 fan을 absolute 모델 결과로 복구한다."""
        if "fan" not in self.recent_off_devices:
            return
        if any(x.get("device") == "fan" for x in self.active_devices):
            return

        state = str(ai_result.get("state", "empty")).lower() if ai_result else "empty"
        state_probs = ai_result.get("state_probs", {}) if ai_result else {}
        on_prob = _safe_float(state_probs.get("on", 0.0))
        abs_device = _normalize_device_name(ai_result.get("device", None)) if ai_result else None
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0)) if ai_result else 0.0

        ok = (
            state == "on" and
            on_prob >= FAN_RECOVERY_MIN_ON_PROB and
            abs_device == "fan" and
            abs_conf >= FAN_RECOVERY_MIN_CONF and
            _is_fan_alive_features(latest)
        )

        if ok:
            self.recovery_hits["fan"] = int(self.recovery_hits.get("fan", 0)) + 1
        else:
            self.recovery_hits["fan"] = max(0, int(self.recovery_hits.get("fan", 0)) - 1)

        if self.recovery_hits.get("fan", 0) >= FAN_RECOVERY_HITS:
            # v18: 직접 active_devices에 append하면 retained_off_slots 때문에 3번째 칸에 FAN_ON이 새로 생길 수 있다.
            # 반드시 _add_active_device()를 통해 같은 fan slot을 재사용하고, 기존 FAN_OFF 잔상/메모리를 지운다.
            before_slots = [int(x.get("slot", 0)) for x in self.off_events if x.get("device") == "fan"]
            if not before_slots:
                before_slots = [int(s) for s, info in self.retained_off_slots.items() if info.get("device") == "fan"]

            added = self._add_active_device(
                "fan",
                abs_conf,
                ai_result.get("device_probs", {}) if ai_result else {},
                event=None,
                source="recent_off_recovery",
            )

            self.recent_off_devices.pop("fan", None)
            self.recovery_hits.pop("fan", None)

            if self.verbose and added:
                slot = self.device_slot_memory.get("fan")
                print(
                    f"[DELTA RECOVERY] FAN restored slot={(int(slot) + 1) if slot is not None else '?'} | "
                    f"abs_conf={abs_conf:.2f}, on_prob={on_prob:.2f}, previous_off_slots={[s + 1 for s in before_slots]}"
                )

    def _recover_dryer_if_needed(self, ai_result, latest):
        """OFF 처리된 dryer가 실제로는 계속 켜져 있으면 같은 slot으로 복구한다."""
        if "dryer" not in self.recent_off_devices:
            return
        if any(x.get("device") == "dryer" for x in self.active_devices):
            return
        if not _is_dryer_alive_features(latest):
            return

        state = str(ai_result.get("state", "empty")).lower() if ai_result else "empty"
        state_probs = ai_result.get("state_probs", {}) if ai_result else {}
        on_prob = _safe_float(state_probs.get("on", 0.0))
        abs_device = _normalize_device_name(ai_result.get("device", None)) if ai_result else None
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0)) if ai_result else 0.0
        device_probs = ai_result.get("device_probs", {}) if ai_result else {}
        cooker_prob = _prob_for(device_probs, "cooker")
        dryer_prob = _prob_for(device_probs, "dryer")

        # v33: 실제 cooker heating이 올라온 상황에서, 남아 있던 DRYER_OFF memory 때문에
        # DRYER가 자동 복구되면 COOKER_ON+FAN_ON+DRYER_ON으로 꼬인다.
        # cooker ON/COOKER_OFF + FAN_ON 문맥이고, 현재 feature가 cooker heating with fan 범위이면
        # dryer recovery를 막고 memory를 서서히 줄인다.
        has_cooker_on = any(x.get("device") == "cooker" and x.get("state") == "on" for x in self.active_devices)
        has_fan_on = self._has_fan_on_context()
        if (
            has_fan_on and
            (has_cooker_on or self._has_cooker_off_context()) and
            _is_real_cooker_heating_with_fan_features(latest) and
            not _is_fast_high_dryer_features(latest) and
            (abs_device == "cooker" or cooker_prob >= dryer_prob)
        ):
            self.recovery_hits["dryer"] = 0
            if self.verbose:
                print(
                    "[DELTA RECOVERY] DRYER restore blocked: real cooker heating with fan suspected | "
                    f"abs_device={abs_device}, cooker_prob={cooker_prob:.2f}, dryer_prob={dryer_prob:.2f}, "
                    f"I={_safe_float(latest.get('Irms_adc', 0.0)):.2f}, "
                    f"Pabs={_safe_float(latest.get('Pabs_mean_proxy', 0.0)):.1f}, "
                    f"H1={_safe_float(latest.get('H1_60_mag', 0.0)):.1f}"
                )
            return

        ok = (
            state == "on" and
            on_prob >= DRYER_RECOVERY_MIN_ON_PROB and
            (abs_device == "dryer" or (abs_conf >= DRYER_RECOVERY_MIN_CONF and not (abs_device == "cooker" and cooker_prob >= dryer_prob)))
        )

        if not ok:
            return

        self.recovery_hits["dryer"] = int(self.recovery_hits.get("dryer", 0)) + 1
        if self.recovery_hits.get("dryer", 0) < DRYER_RECOVERY_HITS:
            return

        slot = None
        for item in self.off_events:
            if item.get("device") == "dryer":
                slot = int(item.get("slot", 0))
                break
        if slot is None:
            slot = self.device_slot_memory.get("dryer")
        if slot is None:
            slot = self._first_free_slot()

        self.off_events = deque([x for x in self.off_events if x.get("device") != "dryer"], maxlen=MAX_ACTIVE_DEVICES)

        self.active_devices.append({
            "device": "dryer",
            "slot": slot,
            "state": "on",
            "hold": 0,
            "conf": max(abs_conf, 0.80),
            "signature": {
                "Pabs_mean_proxy": _safe_float(latest.get("Pabs_mean_proxy", 0.0)),
                "Irms_adc": _safe_float(latest.get("Irms_adc", 0.0)),
                "H1_60_mag": _safe_float(latest.get("H1_60_mag", 0.0)),
                "THD_i": _safe_float(latest.get("THD_i", 0.0)),
            },
            "probs": ai_result.get("device_probs", {}) if ai_result else {},
        })
        self.device_slot_memory["dryer"] = slot
        self._clear_retained_off(device="dryer", slot=slot)
        self.off_events = deque([x for x in self.off_events if x.get("device") != "dryer"], maxlen=MAX_ACTIVE_DEVICES)
        self.recent_off_devices.pop("dryer", None)
        self.recovery_hits.pop("dryer", None)

        if self.verbose:
            print(f"[DELTA RECOVERY] DRYER restored slot={slot + 1} | abs_conf={abs_conf:.2f}, on_prob={on_prob:.2f}")

    def _sync_absolute_device_if_needed(self, ai_result, latest):
        """
        v9 보정:
        - dryer와 fan의 absolute sync 기준을 분리한다.
        - fan 단독은 on_prob 0.70 이상 + fan_conf 0.88 이상 + fan absolute feature가 2회 지속되면 FAN_ON으로 올린다.
        - charger도 active는 허용하되, 확률 우세와 fan/dryer feature 겹침을 검사해서 후보 단계에서 거른다.
        """
        if not ai_result or not latest:
            return

        state = str(ai_result.get("state", "empty")).lower()
        state_probs = ai_result.get("state_probs", {}) or {}
        on_prob = _safe_float(state_probs.get("on", 0.0))
        abs_device = _normalize_device_name(ai_result.get("device", None))
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0))
        device_probs = ai_result.get("device_probs", {}) or {}
        cooker_prob = _prob_for(device_probs, "cooker")
        dryer_prob = _prob_for(device_probs, "dryer")
        fan_prob = _prob_for(device_probs, "fan")

        # v10: charger absolute sync도 허용하되, fan/dryer와 애매하게 겹치면 후보 자체를 버린다.
        if abs_device == "charger":
            ok, reason = _charger_absolute_candidate_is_reliable(
                latest,
                ai_result.get("device_probs", {}) or {},
                abs_conf,
                on_prob,
            )
            if not ok:
                self.charger_abs_sync_hits = max(0, int(getattr(self, "charger_abs_sync_hits", 0)) - 1)
                if self.verbose and abs_conf >= 0.60:
                    print(f"[ABS DEVICE GUARD] CHARGER candidate rejected | reason={reason} | conf={abs_conf:.2f}")
                # charger가 아니면 아래 fan/dryer sync 판단은 계속 진행할 수 있도록 return하지 않는다.
            else:
                self.charger_abs_sync_hits = int(getattr(self, "charger_abs_sync_hits", 0)) + 1
                if self.charger_abs_sync_hits >= CHARGER_ABS_SYNC_HITS_REQUIRED:
                    self._add_active_device(
                        "charger",
                        max(abs_conf, CHARGER_ACTIVE_MIN_CONF),
                        ai_result.get("device_probs", {}) or {},
                        event=None,
                        source="absolute_sync",
                    )
                    self.charger_abs_sync_hits = 0
                    return

        # v23: cooker absolute sync.
        # cooker는 delta가 dryer/fan 변화에 묻힐 수 있으므로, 모델이 cooker를 일정 block 이상 보면 active에 올린다.
        cooker_already_active = any(x.get("device") == "cooker" for x in self.active_devices)

        # v26: COOKER_OFF 위에 fan이 켜진 profile은 RF가 계속 cooker로 보더라도 FAN_ON으로 보정한다.
        if (
            self._has_cooker_off_context() and
            not any(x.get("device") == "fan" and x.get("state") == "on" for x in self.active_devices) and
            _is_cooker_plus_fan_features(latest)
        ):
            self.cooker_fan_abs_hits = int(getattr(self, "cooker_fan_abs_hits", 0)) + 1
            if self.cooker_fan_abs_hits >= COOKER_PLUS_FAN_HITS_REQUIRED:
                self._add_active_device(
                    "fan",
                    max(fan_prob, 0.80),
                    {"fan": max(fan_prob, 0.80), "cooker": cooker_prob},
                    event=None,
                    source="cooker_off_fan_absolute",
                )
                self.cooker_fan_abs_hits = 0
                return
        else:
            self.cooker_fan_abs_hits = max(0, int(getattr(self, "cooker_fan_abs_hits", 0)) - 1)

        # cooker standby/off profile은 absolute model이 cooker라고 해도 COOKER_OFF로 표시한다.
        # 단, cooker_off+fan profile은 위에서 FAN_ON 보정을 먼저 수행한다.
        if abs_device == "cooker" and _is_cooker_standby_off_features(latest):
            self.cooker_abs_sync_hits = 0
            # v25: cooker 단독 실험에서 잘못 올라간 DRYER_ON이 남아 있는데
            # 현재값이 dryer_alive가 아니면 같이 OFF로 내려준다.
            if any(x.get("device") == "dryer" for x in self.active_devices) and not _is_dryer_alive_features(latest):
                removed = None
                remain = []
                for item in self.active_devices:
                    if removed is None and item.get("device") == "dryer":
                        removed = item
                    else:
                        remain.append(item)
                self.active_devices = remain
                if removed is not None:
                    slot = int(removed.get("slot", 0))
                    if USE_DEVICE_SLOT_MEMORY:
                        self.device_slot_memory["dryer"] = slot
                    self.off_events.append({"device": "dryer", "slot": slot, "hold": OFF_HOLD_BLOCKS, "conf": 0.80, "source": "cooker_standby_cleared_false_dryer"})
                    self.recent_off_devices["dryer"] = RECENT_OFF_MEMORY_BLOCKS
                    self.recovery_hits["dryer"] = 0
                    # fake dryer를 내린 경우 FAN 복구 창을 열지 않는다.
                    self.post_dryer_off_recovery_left = 0
                    self.post_dryer_off_fan_hits = 0
                    if self.verbose:
                        print("[ABS DEVICE GUARD] false DRYER moved OFF: cooker standby/off remains")
            self._mark_device_off("cooker", conf=abs_conf, source="cooker_standby_absolute")
            return

        if (
            not cooker_already_active and
            state == "on" and
            on_prob >= COOKER_ABS_SYNC_MIN_ON_PROB and
            abs_device == "cooker" and
            abs_conf >= COOKER_ABS_SYNC_MIN_CONF and
            _is_cooker_heating_features(latest) and
            not self._should_block_cooker_on_due_to_dryer_context(latest)
        ):
            self.cooker_abs_sync_hits = int(getattr(self, "cooker_abs_sync_hits", 0)) + 1
        else:
            if (
                not cooker_already_active and
                abs_device == "cooker" and
                _is_cooker_heating_features(latest) and
                self._should_block_cooker_on_due_to_dryer_context(latest)
            ):
                if self.verbose:
                    print(
                        "[ABS DEVICE GUARD] COOKER sync blocked: dryer mode/restart over COOKER_OFF suspected | "
                        f"abs_conf={abs_conf:.2f}, cooker_prob={cooker_prob:.2f}, dryer_prob={dryer_prob:.2f}, "
                        f"I={_safe_float(latest.get('Irms_adc', 0.0)):.2f}, "
                        f"Pabs={_safe_float(latest.get('Pabs_mean_proxy', 0.0)):.1f}, "
                        f"H1={_safe_float(latest.get('H1_60_mag', 0.0)):.1f}"
                    )
            self.cooker_abs_sync_hits = max(0, int(getattr(self, "cooker_abs_sync_hits", 0)) - 1)

        if self.cooker_abs_sync_hits >= COOKER_ABS_SYNC_HITS_REQUIRED:
            self._add_active_device(
                "cooker",
                max(abs_conf, COOKER_ABS_SYNC_MIN_CONF),
                ai_result.get("device_probs", {}) or {},
                event=None,
                source="absolute_sync_heating",
            )
            self.cooker_abs_sync_hits = 0
            return

        # v25: 밥솥 취사/가열 중에는 RF absolute 모델이 가끔 dryer로 흔들린다.
        # 이때 fast_absolute_sync가 DRYER_ON을 새 slot에 추가하면,
        # cooker 단독 실험에서도 COOKER_ON + DRYER_ON이 된다.
        # 이미 cooker가 active이고 현재 feature가 cooker heating 영역이면,
        # 별도의 delta ON이 아닌 absolute dryer sync는 cooker 흔들림으로 보고 차단한다.
        cooker_heating_active = (
            cooker_already_active and
            _is_cooker_heating_features(latest) and
            not any(x.get("device") == "dryer" and x.get("state") == "on" for x in self.active_devices)
        )
        if cooker_heating_active and abs_device == "dryer" and cooker_prob >= 0.30:
            self.dryer_fast_sync_hits = 0
            self._update_active_signature_from_latest("cooker", latest, max(abs_conf, cooker_prob, 0.80))
            if self.verbose:
                print(
                    "[ABS DEVICE GUARD] DRYER sync blocked: cooker heating context | "
                    f"abs_conf={abs_conf:.2f}, dryer_prob={dryer_prob:.2f}, cooker_prob={cooker_prob:.2f}, "
                    f"I={_safe_float(latest.get('Irms_adc', 0.0)):.2f}, "
                    f"Pabs={_safe_float(latest.get('Pabs_mean_proxy', 0.0)):.1f}, "
                    f"H1={_safe_float(latest.get('H1_60_mag', 0.0)):.1f}"
                )
            return

        # standalone fan absolute sync.
        # 기존 v8은 dryer 기준 on_prob(0.80)를 같이 써서, 로그상 fan 단독 구간(on_prob 0.74~0.79)을 놓쳤다.
        if (
            state == "on" and
            on_prob >= FAN_ABS_SYNC_MIN_ON_PROB and
            abs_device == "fan" and
            abs_conf >= FAN_ABS_SYNC_MIN_CONF and
            _is_fan_alive_features(latest) and
            not any(x.get("device") == "dryer" and x.get("state") == "on" for x in self.active_devices) and
            not any(x.get("device") == "fan" and x.get("state") == "on" for x in self.active_devices)
        ):
            self.fan_abs_sync_hits = int(getattr(self, "fan_abs_sync_hits", 0)) + 1
        else:
            self.fan_abs_sync_hits = max(0, int(getattr(self, "fan_abs_sync_hits", 0)) - 1)

        if self.fan_abs_sync_hits >= FAN_ABS_SYNC_HITS_REQUIRED:
            self._add_active_device(
                "fan",
                abs_conf,
                ai_result.get("device_probs", {}) or {},
                event=None,
                source="absolute_sync",
            )
            self.fan_abs_sync_hits = 0
            return

        # v15: dryer 빠른 absolute sync.
        # on_prob가 0.45~0.50에서 머물러도 feature가 명백히 dryer급이면 2 block 확인 후 DRYER_ON으로 올린다.
        dryer_already_active = any(x.get("device") == "dryer" for x in self.active_devices)
        if (
            not dryer_already_active and
            abs_device == "dryer" and
            abs_conf >= DRYER_FAST_SYNC_MIN_CONF and
            on_prob >= DRYER_FAST_SYNC_MIN_ON_PROB and
            _is_fast_dryer_sync_features(latest)
        ):
            self.dryer_fast_sync_hits = int(getattr(self, "dryer_fast_sync_hits", 0)) + 1
        else:
            self.dryer_fast_sync_hits = max(0, int(getattr(self, "dryer_fast_sync_hits", 0)) - 1)

        if self.dryer_fast_sync_hits >= DRYER_FAST_SYNC_HITS_REQUIRED:
            self._add_active_device(
                "dryer",
                max(abs_conf, 0.80),
                ai_result.get("device_probs", {}) or {},
                event=None,
                source="fast_absolute_sync",
            )
            self.dryer_fast_sync_hits = 0
            return

        # dryer absolute sync는 기존처럼 더 강한 on_prob/conf 기준을 사용한다.
        if state != "on" or on_prob < DRYER_ABS_SYNC_MIN_ON_PROB:
            return

        if (
            abs_device == "dryer" and
            abs_conf >= DRYER_ABS_SYNC_MIN_CONF and
            _is_dryer_alive_features(latest) and
            not any(x.get("device") == "dryer" for x in self.active_devices)
        ):
            self._add_active_device(
                "dryer",
                abs_conf,
                ai_result.get("device_probs", {}) or {},
                event=None,
                source="absolute_sync",
            )
            return
    def _prune_stale_active_devices(self, ai_result, latest):
        """
        v6 보정:
        active list에 남은 유령 fan/dryer 제거.
        특히 dryer OFF 뒤 latest가 idle인데 FAN_ON이 계속 남는 문제를 제거한다.
        """
        if not latest:
            return

        idle = _is_idle_features(latest)
        if not idle:
            return

        if not self.active_devices:
            return

        removed = []
        kept = []
        for item in self.active_devices:
            dev = item.get("device")
            if dev in TRACKED_DEVICE_NAMES:
                removed.append(item)
            else:
                kept.append(item)

        if not removed:
            return

        self.active_devices = kept
        for item in removed:
            dev = item.get("device")
            slot = int(item.get("slot", 0))
            if USE_DEVICE_SLOT_MEMORY and dev is not None:
                self.device_slot_memory[dev] = slot

            # v12: stale/idle 제거는 실제 사용자가 기기를 끈 상황일 수 있으므로
            #      바로 EMPTY로 보내지 말고 OFF_HOLD_BLOCKS 동안 *_OFF를 표시한다.
            if dev in TRACKED_DEVICE_NAMES:
                self.off_events.append({
                    "device": dev,
                    "slot": slot,
                    "hold": OFF_HOLD_BLOCKS,
                    "conf": _safe_float(item.get("conf", 0.80)),
                    "source": "stale_idle_clear",
                })
                self.recent_off_devices[dev] = RECENT_OFF_MEMORY_BLOCKS
                self.recovery_hits[dev] = 0

        if self.verbose:
            names = ", ".join([str(x.get("device", "?")).upper() for x in removed])
            print(f"[DELTA STALE] moved active {names} to OFF: latest is idle")


    def _update_dryer_baseline(self, ai_result, latest):
        """DRYER_ON이 안정적으로 유지되는 구간의 기준선을 저장한다.

        fan이 active이거나 pending이면 baseline을 갱신하지 않는다. fan 성분이 baseline에 흡수되면
        residual 검출이 불가능해지기 때문이다.
        """
        if latest is None:
            return

        has_dryer = any(x.get("device") == "dryer" and x.get("state") == "on" for x in self.active_devices)
        has_fan = any(x.get("device") == "fan" and x.get("state") == "on" for x in self.active_devices)
        if not has_dryer or has_fan or self.pending_on is not None:
            return

        # v14: fan-like 잔차가 보이는 동안 baseline을 계속 갱신하면
        # fan 성분이 dryer_baseline에 흡수되어 이후 FAN_ON을 놓친다.
        if self.dryer_baseline_freeze_left > 0:
            self.dryer_baseline_freeze_left -= 1
            return
        else:
            self.dryer_baseline_frozen = None

        state_probs = ai_result.get("state_probs", {}) if ai_result else {}
        on_prob = _safe_float(state_probs.get("on", 0.0))
        abs_device = _normalize_device_name(ai_result.get("device", None)) if ai_result else None
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0)) if ai_result else 0.0

        if (
            abs_device == "dryer" and
            abs_conf >= DRYER_BASELINE_ABS_CONF_MIN and
            on_prob >= DRYER_BASELINE_ON_PROB_MIN and
            _is_dryer_alive_features(latest)
        ):
            self.dryer_baseline_rows.append(dict(latest))
            if len(self.dryer_baseline_rows) >= DRYER_BASELINE_MIN_BLOCKS:
                self.dryer_baseline = _mean_features(list(self.dryer_baseline_rows))

    def _detect_fan_by_dryer_residual(self, ai_result, latest):
        """DRYER_ON 기준선 위에 fan 크기의 잔차가 지속되면 FAN_ON을 추가한다.

        v14 개선:
        - 고출력 dryer에서는 fan 변화량이 baseline 갱신에 흡수되기 쉬우므로
          fan-like residual이 보이면 dryer baseline을 잠깐 freeze한다.
        - strong residual은 기존처럼 빠르게 확정하고, soft residual은 더 긴 연속 hit 후 확정한다.
        """
        if latest is None or self.dryer_baseline is None:
            self.fan_residual_hits = 0
            self.fan_residual_soft_hits = 0
            return

        has_dryer = any(x.get("device") == "dryer" and x.get("state") == "on" for x in self.active_devices)
        has_fan = any(x.get("device") == "fan" and x.get("state") == "on" for x in self.active_devices)
        if not has_dryer or has_fan:
            self.fan_residual_hits = 0
            self.fan_residual_soft_hits = 0
            return

        # v19: FAN_OFF 직후 ghost residual은 경계하되, 사용자가 실제로 다시 켜는 경우까지 막지는 않는다.
        # 따라서 recent_off 상태를 기억만 하고, 아래에서 residual hit 수를 더 요구하는 방식으로 처리한다.
        recent_fan_off_active = bool(BLOCK_RESIDUAL_FAN_READD_WHEN_RECENTLY_OFF and "fan" in self.recent_off_devices)

        state_probs = ai_result.get("state_probs", {}) if ai_result else {}
        on_prob = _safe_float(state_probs.get("on", 0.0))
        if on_prob < 0.80:
            self.fan_residual_hits = max(0, self.fan_residual_hits - 1)
            self.fan_residual_soft_hits = max(0, self.fan_residual_soft_hits - 1)
            return

        # freeze가 걸린 상태라면 최초 의심 시점의 baseline을 기준으로 계속 비교한다.
        base = self.dryer_baseline_frozen or self.dryer_baseline
        res = _sub_feature_triplet(latest, base)
        strong = _is_fan_residual_triplet(res)
        soft = _is_soft_fan_residual_triplet(res)

        if strong or soft:
            if self.dryer_baseline_frozen is None:
                self.dryer_baseline_frozen = dict(self.dryer_baseline)
            self.dryer_baseline_freeze_left = DRYER_BASELINE_FREEZE_BLOCKS

        if strong:
            self.fan_residual_hits += 1
            self.fan_residual_soft_hits = max(0, self.fan_residual_soft_hits - 1)
        elif soft:
            self.fan_residual_soft_hits += 1
            self.fan_residual_hits = max(0, self.fan_residual_hits - 1)
        else:
            self.fan_residual_hits = max(0, self.fan_residual_hits - 1)
            self.fan_residual_soft_hits = max(0, self.fan_residual_soft_hits - 1)

        required_strong_hits = FAN_RESIDUAL_HITS_REQUIRED
        required_soft_hits = FAN_RESIDUAL_SOFT_HITS_REQUIRED
        if recent_fan_off_active:
            # OFF 직후 ghost 복구는 막되, 사용자가 실제로 다시 켠 경우처럼 residual이 계속 유지되면 허용한다.
            required_strong_hits += FAN_READD_AFTER_OFF_EXTRA_HITS
            required_soft_hits += FAN_READD_AFTER_OFF_EXTRA_HITS

        should_add = (
            self.fan_residual_hits >= required_strong_hits or
            self.fan_residual_soft_hits >= required_soft_hits
        )

        if recent_fan_off_active and not should_add:
            if self.verbose:
                print(
                    "[DELTA RESIDUAL] FAN re-add waiting: recent FAN_OFF memory active | "
                    f"hits={self.fan_residual_hits}/{required_strong_hits}, "
                    f"soft={self.fan_residual_soft_hits}/{required_soft_hits}"
                )

        if should_add:
            event = {
                "type": "on",
                "score": 1.0,
                "delta": {
                    "Pabs_mean_proxy": max(0.0, res["Pabs_mean_proxy"]),
                    "Irms_adc": max(0.0, res["Irms_adc"]),
                    "H1_60_mag": max(0.0, res["H1_60_mag"]),
                    "THD_i": 0.0,
                },
                "old_mean": base,
                "new_mean": latest,
                "old_rows": [],
                "new_rows": [],
            }
            conf = 0.88 if self.fan_residual_hits >= FAN_RESIDUAL_HITS_REQUIRED else 0.82
            self._add_active_device("fan", conf, {"fan": conf, "dryer": 0.12, "charger": 0.02}, event, source="dryer_residual")
            self.fan_residual_hits = 0
            self.fan_residual_soft_hits = 0
            self.dryer_baseline_freeze_left = 0
            self.dryer_baseline_frozen = None
            if self.verbose:
                mode = "strong" if conf >= 0.88 else "soft"
                print(
                    f"[DELTA RESIDUAL] FAN restored/added over DRYER baseline({mode}) | "
                    f"rPabs={res['Pabs_mean_proxy']:.1f}, rI={res['Irms_adc']:.2f}, rH1={res['H1_60_mag']:.1f}"
                )

    def _move_active_fan_to_off(self, conf=0.80, source="fan_negative_residual_missing"):
        """v22: residual 기반으로 FAN_OFF를 확정할 때 공통으로 사용하는 제거 함수."""
        removed_slots = []
        kept = []
        for item in self.active_devices:
            if item.get("device") == "fan":
                slot = int(item.get("slot", 0))
                removed_slots.append(slot)
                if USE_DEVICE_SLOT_MEMORY:
                    self.device_slot_memory["fan"] = slot
            else:
                kept.append(item)

        if not removed_slots:
            return False

        self.active_devices = kept
        for slot in removed_slots:
            self.off_events.append({
                "device": "fan",
                "slot": slot,
                "hold": OFF_HOLD_BLOCKS,
                "conf": max(_safe_float(conf, 0.0), 0.80),
                "source": source,
            })
            self.recent_off_devices["fan"] = RECENT_OFF_MEMORY_BLOCKS
            self.recovery_hits["fan"] = 0
            if USE_DEVICE_SLOT_MEMORY:
                self.device_slot_memory["fan"] = slot

        return True

    def _detect_fan_off_by_dryer_residual(self, ai_result, latest):
        """DRYER_ON + FAN_ON 상태에서 fan 잔차가 사라지면 FAN_OFF로 처리한다.

        v10까지는 FAN_ON을 추가하는 residual/absolute 복구는 있었지만,
        드라이기는 계속 켜져 있고 fan만 꺼지는 경우에는 큰 OFF delta가 드라이기 변동에 묻혀
        active list의 FAN_ON이 유지될 수 있었다. v11에서는 dryer_baseline을 기준으로
        현재값 - dryer_baseline의 잔차가 fan 범위가 아닌 상태가 연속되면 fan만 제거한다.
        """
        if latest is None or self.dryer_baseline is None:
            self.fan_residual_absent_hits = 0
            return

        has_dryer = any(x.get("device") == "dryer" and x.get("state") == "on" for x in self.active_devices)
        has_fan = any(x.get("device") == "fan" and x.get("state") == "on" for x in self.active_devices)
        if not has_dryer or not has_fan:
            self.fan_residual_absent_hits = 0
            return

        # 드라이기 자체가 꺼진 상황이면 이 함수가 아니라 기존 OFF DRYER / post-dryer recovery가 처리한다.
        if not _is_dryer_alive_features(latest):
            self.fan_residual_absent_hits = 0
            return

        state_probs = ai_result.get("state_probs", {}) if ai_result else {}
        on_prob = _safe_float(state_probs.get("on", 0.0))
        abs_device = _normalize_device_name(ai_result.get("device", None)) if ai_result else None
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0)) if ai_result else 0.0
        device_probs = ai_result.get("device_probs", {}) if ai_result else {}
        fan_prob = _prob_for(device_probs, "fan")
        dryer_prob = _prob_for(device_probs, "dryer")

        # 아직 전체 상태가 불안정하면 판단을 유예한다.
        if on_prob < FAN_OFF_RESIDUAL_ON_PROB_MIN:
            self.fan_residual_absent_hits = max(0, self.fan_residual_absent_hits - 1)
            return

        # residual 계산: 양수 residual이 fan 크기로 남아 있으면 fan은 아직 켜진 상태로 본다.
        res = _sub_feature_triplet(latest, self.dryer_baseline)

        # v19: residual이 음수인 상태를 FAN_OFF로 처리하지 않는다.
        # FAN_ON 직후 dryer baseline이 더 높은 모드로 잡히면 현재값-baseline이 음수가 되는데,
        # 이것을 FAN_OFF로 보면 켜진 선풍기가 바로 묻힌다.
        negative_baseline_shift = (
            res["Pabs_mean_proxy"] <= -DRYER_MODE_SHIFT_NEG_PABS or
            res["Irms_adc"] <= -DRYER_MODE_SHIFT_NEG_IRMS or
            res["H1_60_mag"] <= -DRYER_MODE_SHIFT_NEG_H1
        )
        if negative_baseline_shift:
            self.fan_residual_absent_hits = 0

            # v22: 드라이기 모드 전환 직후의 음수 residual은 기존처럼 보호한다.
            # 하지만 guard 시간이 아닌데 dryer만 강하게 보이고 fan 확률이 낮은 음수 residual이
            # 여러 block 지속되면 실제 FAN_OFF로 처리한다.
            fan_items = [x for x in self.active_devices if x.get("device") == "fan"]
            fan_age = max([int(x.get("age", 0)) for x in fan_items] or [0])
            dryer_only_supported = (
                self.dryer_mode_shift_guard <= 0 and
                fan_age >= FAN_OFF_GRACE_BLOCKS and
                abs_device == "dryer" and
                abs_conf >= FAN_OFF_NEGATIVE_DRYER_CONF_MIN and
                fan_prob <= FAN_OFF_NEGATIVE_FAN_PROB_MAX and
                _is_dryer_alive_features(latest)
            )

            # v30: COOKER_OFF + FAN_ON + fast_high DRYER_ON에서는 dryer baseline 자체가 크게 흔들려
            # 음수 residual이 계속 쌓일 수 있다. 이 경우 실제 FAN_OFF로 확정하지 않고 보호한다.
            if self._has_cooker_off_context() and self._has_fan_on_context() and _is_fast_high_dryer_features(latest):
                self.fan_negative_residual_absent_hits = 0
                if self.verbose:
                    print(
                        "[DELTA RESIDUAL] FAN_OFF skipped: fast_high dryer fluctuation protected(v30) | "
                        f"rPabs={res['Pabs_mean_proxy']:.1f}, "
                        f"rI={res['Irms_adc']:.2f}, "
                        f"rH1={res['H1_60_mag']:.1f}"
                    )
                return

            if dryer_only_supported:
                self.fan_negative_residual_absent_hits += 1
            else:
                self.fan_negative_residual_absent_hits = 0

            if self.fan_negative_residual_absent_hits >= FAN_OFF_NEGATIVE_RESIDUAL_HITS_REQUIRED:
                removed = self._move_active_fan_to_off(
                    conf=max(fan_prob, 0.80),
                    source="fan_negative_residual_missing_v22",
                )
                self.fan_negative_residual_absent_hits = 0
                if self.verbose and removed:
                    print(
                        "[DELTA RESIDUAL] OFF FAN by negative residual missing(v22) | "
                        f"rPabs={res['Pabs_mean_proxy']:.1f}, "
                        f"rI={res['Irms_adc']:.2f}, "
                        f"rH1={res['H1_60_mag']:.1f}, "
                        f"abs_conf={abs_conf:.2f}, fan_prob={fan_prob:.2f}"
                    )
                return

            if self.verbose:
                print(
                    "[DELTA RESIDUAL] FAN_OFF skipped: dryer baseline shifted negative(v22 guard) | "
                    f"rPabs={res['Pabs_mean_proxy']:.1f}, "
                    f"rI={res['Irms_adc']:.2f}, "
                    f"rH1={res['H1_60_mag']:.1f}, "
                    f"neg_hits={self.fan_negative_residual_absent_hits}/{FAN_OFF_NEGATIVE_RESIDUAL_HITS_REQUIRED}, "
                    f"mode_guard={self.dryer_mode_shift_guard}"
                )
            return

        self.fan_negative_residual_absent_hits = 0
        residual_fan_like = _is_fan_residual_triplet(res)

        # 절대 feature가 fan 단독 범위면 드라이기가 꺼진 뒤 fan만 남은 상태일 수 있으므로 여기서 끄지 않는다.
        if _is_fan_alive_features(latest) and not _is_dryer_alive_features(latest):
            self.fan_residual_absent_hits = 0
            return

        # 모델이 fan을 강하게 지지하면 잔차가 조금 작아도 유지한다.
        if abs_device == "fan" and abs_conf >= 0.75:
            self.fan_residual_absent_hits = 0
            return
        if fan_prob >= 0.55 and fan_prob >= dryer_prob + 0.15:
            self.fan_residual_absent_hits = 0
            return

        # 드라이기 우세 + fan residual 사라짐이면 fan OFF 후보 카운트 증가.
        dryer_supported = (
            (abs_device == "dryer" and abs_conf >= FAN_OFF_RESIDUAL_DRYER_CONF_MIN) or
            (dryer_prob >= 0.70 and dryer_prob >= fan_prob + 0.25) or
            _is_dryer_alive_features(latest)
        )

        residual_absent = (
            not residual_fan_like and
            max(0.0, res.get("Pabs_mean_proxy", 0.0)) <= FAN_OFF_RESIDUAL_PABS_MAX and
            max(0.0, res.get("Irms_adc", 0.0)) <= FAN_OFF_RESIDUAL_IRMS_MAX and
            max(0.0, res.get("H1_60_mag", 0.0)) <= FAN_OFF_RESIDUAL_H1_MAX
        )

        # 방금 FAN_ON으로 확정된 직후 몇 block은 dryer baseline이 아직 맞지 않아 잔차가 튈 수 있으므로 유예한다.
        fan_items = [x for x in self.active_devices if x.get("device") == "fan"]
        fan_age = max([int(x.get("age", 0)) for x in fan_items] or [0])
        if fan_age < FAN_OFF_GRACE_BLOCKS:
            self.fan_residual_absent_hits = 0
            return

        if dryer_supported and residual_absent:
            self.fan_residual_absent_hits += 1
        else:
            self.fan_residual_absent_hits = max(0, self.fan_residual_absent_hits - 1)

        if self.fan_residual_absent_hits < FAN_OFF_RESIDUAL_MISSING_HITS_REQUIRED:
            return

        # fan만 제거하고 dryer는 유지한다.
        removed = None
        remain = []
        for item in self.active_devices:
            if removed is None and item.get("device") == "fan":
                removed = item
            else:
                remain.append(item)
        if removed is None:
            self.fan_residual_absent_hits = 0
            return

        self.active_devices = remain
        slot = int(removed.get("slot", 0))
        if USE_DEVICE_SLOT_MEMORY:
            self.device_slot_memory["fan"] = slot
        self.off_events.append({"device": "fan", "slot": slot, "hold": OFF_HOLD_BLOCKS, "conf": max(fan_prob, 0.80)})
        self.recent_off_devices["fan"] = RECENT_OFF_MEMORY_BLOCKS
        self.recovery_hits["fan"] = 0
        self.fan_residual_absent_hits = 0
        self.fan_residual_hits = 0

        if self.verbose:
            print(
                f"[DELTA RESIDUAL] OFF FAN slot={slot + 1} source=dryer_residual_missing | "
                f"rPabs={res['Pabs_mean_proxy']:.1f}, rI={res['Irms_adc']:.2f}, rH1={res['H1_60_mag']:.1f} | "
                f"dryer_prob={dryer_prob:.2f}, fan_prob={fan_prob:.2f}"
            )

    def _recover_fan_after_dryer_off(self, ai_result, latest):
        """드라이기 OFF 후 fan만 남았을 때 absolute feature로 FAN_ON 복구."""
        if latest is None:
            return
        if any(x.get("device") == "fan" and x.get("state") == "on" for x in self.active_devices):
            self.post_dryer_off_fan_hits = 0
            return
        if self.post_dryer_off_recovery_left <= 0:
            self.post_dryer_off_fan_hits = 0
            return

        state = str(ai_result.get("state", "empty")).lower() if ai_result else "empty"
        state_probs = ai_result.get("state_probs", {}) if ai_result else {}
        on_prob = _safe_float(state_probs.get("on", 0.0))
        abs_device = _normalize_device_name(ai_result.get("device", None)) if ai_result else None
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0)) if ai_result else 0.0
        device_probs = ai_result.get("device_probs", {}) if ai_result else {}
        cooker_prob = _prob_for(device_probs, "cooker")
        fan_prob = _prob_for(device_probs, "fan")

        # v25: cooker_off/standby profile이 fan 단독 범위와 겹친다.
        # fake DRYER_OFF 이후 이 값을 fan_like로 해석하면 FAN_ON 유령 복구가 생긴다.
        # 현재 absolute 모델이 cooker를 지지하거나 cooker standby/off 범위면 FAN 복구를 막는다.
        if (
            _is_cooker_standby_off_features(latest) and
            not _is_cooker_plus_fan_features(latest) and
            (abs_device == "cooker" or cooker_prob >= fan_prob)
        ):
            self.post_dryer_off_fan_hits = 0
            if self.verbose:
                print(
                    "[DELTA RECOVERY] FAN recovery blocked: cooker standby/off profile | "
                    f"abs_device={abs_device}, cooker_prob={cooker_prob:.2f}, fan_prob={fan_prob:.2f}, "
                    f"I={_safe_float(latest.get('Irms_adc', 0.0)):.2f}, "
                    f"Pabs={_safe_float(latest.get('Pabs_mean_proxy', 0.0)):.1f}, "
                    f"H1={_safe_float(latest.get('H1_60_mag', 0.0)):.1f}"
                )
            return

        # fan 단독 범위가 명확하면 모델 confidence가 낮아도 복구한다.
        fan_like = _is_fan_alive_features(latest)
        model_support = (abs_device == "fan" and abs_conf >= POST_DRYER_OFF_FAN_ABS_CONF_MIN)
        state_support = (state == "on" or on_prob >= POST_DRYER_OFF_FAN_ON_PROB_MIN)

        if fan_like and (state_support or model_support):
            self.post_dryer_off_fan_hits += 1
        else:
            self.post_dryer_off_fan_hits = max(0, self.post_dryer_off_fan_hits - 1)

        if self.post_dryer_off_fan_hits >= POST_DRYER_OFF_FAN_HITS_REQUIRED:
            self._add_active_device("fan", max(abs_conf, 0.80), {"fan": max(abs_conf, 0.80)}, None, source="post_dryer_off_absolute")
            self.post_dryer_off_fan_hits = 0
            if self.verbose:
                print(
                    "[DELTA RECOVERY] FAN restored after DRYER_OFF by absolute feature | "
                    f"I={_safe_float(latest.get('Irms_adc', 0.0)):.2f}, "
                    f"Pabs={_safe_float(latest.get('Pabs_mean_proxy', 0.0)):.1f}, "
                    f"H1={_safe_float(latest.get('H1_60_mag', 0.0)):.1f}"
                )


    def _reconcile_signature_stack(self, ai_result, latest):
        """
        v7 핵심 예외 로직.
        active_devices를 단순 이벤트 결과로만 믿지 않고 현재 absolute feature와 다시 맞춘다.
        - 현재 값이 idle이면 active stack 전체를 정리
        - dryer가 우세한데 fan이 pending_confirm으로 붙어 있으면 fan을 false positive로 제거
        """
        if latest is None:
            return

        # active age 증가
        for item in self.active_devices:
            item["age"] = int(item.get("age", 0)) + 1

        # 1) idle인데 active가 남아 있으면 stack 정리
        if _is_idle_features(latest):
            self.idle_clear_hits += 1
        else:
            self.idle_clear_hits = 0

        if self.idle_clear_hits >= IDLE_CLEAR_HITS_REQUIRED and self.active_devices:
            removed = list(self.active_devices)
            self.active_devices = []
            self.pending_on = None

            # v12: idle 정리로 active를 제거하더라도 UI가 바로 EMPTY로 튀지 않게
            #      짧은 OFF 잔상을 남긴다. 이전 v11은 여기서 off_events까지 비워서
            #      FAN_ON -> EMPTY로 바로 바뀌는 문제가 있었다.
            for item in removed:
                dev = item.get("device")
                slot = int(item.get("slot", 0))
                if USE_DEVICE_SLOT_MEMORY and dev is not None:
                    self.device_slot_memory[dev] = slot
                if dev in TRACKED_DEVICE_NAMES:
                    self.off_events.append({
                        "device": dev,
                        "slot": slot,
                        "hold": OFF_HOLD_BLOCKS,
                        "conf": _safe_float(item.get("conf", 0.80)),
                        "source": "idle_stack_clear",
                    })
                    self.recent_off_devices[dev] = RECENT_OFF_MEMORY_BLOCKS
                    self.recovery_hits[dev] = 0

            if self.verbose:
                names = ", ".join([str(x.get("device", "?")).upper() for x in removed])
                print(f"[DELTA STACK] moved active stack to OFF because latest is idle: {names}")
            return

        # 2) v29: 이미 false COOKER_ON이 active에 올라간 경우도 즉시 COOKER_OFF로 되돌린다.
        # fast_high 구간에서는 v28의 사전 차단을 우회해도 여기서 한 번 더 정리한다.
        has_dryer = any(x.get("device") == "dryer" for x in self.active_devices)
        has_fan = any(x.get("device") == "fan" for x in self.active_devices)
        has_cooker = any(x.get("device") == "cooker" for x in self.active_devices)
        if has_cooker and (has_dryer or self._has_dryer_context()) and has_fan and self._should_block_cooker_on_due_to_dryer_context(latest):
            self._mark_device_off("cooker", conf=0.90, source="reconciled_false_cooker_fast_dryer")
            if self.verbose:
                print(
                    "[DELTA STACK] COOKER_ON -> COOKER_OFF: dryer fast_high/mode change over COOKER_OFF suspected | "
                    f"I={_safe_float(latest.get('Irms_adc', 0.0)):.2f}, "
                    f"Pabs={_safe_float(latest.get('Pabs_mean_proxy', 0.0)):.1f}, "
                    f"H1={_safe_float(latest.get('H1_60_mag', 0.0)):.1f}"
                )
            return

        # 3) DRYER + FAN이 같이 있는데 absolute가 강하게 dryer만 보고 있으면 FAN은 드라이기 변동 오검출일 가능성이 큼
        if not (has_dryer and has_fan):
            self.dryer_dominant_fan_false_hits = 0
            return

        abs_device = _normalize_device_name(ai_result.get("device", None)) if ai_result else None
        abs_conf = _safe_float(ai_result.get("device_conf", 0.0)) if ai_result else 0.0
        dev_probs = ai_result.get("device_probs", {}) if ai_result else {}
        fan_prob = _safe_float(dev_probs.get("fan", 0.0))

        # fan이 진짜 켜져 있으면 대개 전체 feature가 fan 단독 영역으로 내려가거나 absolute fan이 강해지는 구간이 생긴다.
        # 반대로 dryer 고출력/중출력인데 absolute dryer가 우세하면 fan은 제거한다.
        # v8: dryer_residual/post_dryer_off_absolute로 확정된 fan은 absolute 모델이 dryer를 계속 보더라도
        # 전체 CT 구조상 정상일 수 있다. 이 경우 바로 false fan으로 제거하지 않는다.
        has_protected_fan = any(
            x.get("device") == "fan" and x.get("source") in [
                "absolute_sync",
                "pending_confirm",
                "dryer_residual",
                "post_dryer_off_absolute",
                "high_dryer_axis",
                # v27: COOKER_OFF 위에서 보정으로 잡은 FAN은,
                # 드라이기를 켜는 순간 absolute 모델이 dryer만 보더라도 실제 FAN_ON일 수 있다.
                # 따라서 dryer dominant라는 이유만으로 FAN_OFF로 내리지 않는다.
                "cooker_off_fan_absolute",
                "cooker_off_fan_delta",
            ]
            for x in self.active_devices
        )

        # v17: 전체 CT 하나만 쓰는 구조에서는 DRYER fast_high가 켜지면 absolute model이
        # dryer만 강하게 보는 것이 정상이다. 이 이유만으로 기존 FAN_ON을 조용히 삭제하면,
        # 실제 FAN OFF 순간에 FAN_OFF 잔상이 남지 않고 몇 초 뒤 ghost FAN_ON이 재생성된다.
        if PROTECT_TRACKED_FAN_WHEN_DRYER_DOMINANT and has_protected_fan:
            self.dryer_dominant_fan_false_hits = 0
        elif abs_device == "dryer" and abs_conf >= DRYER_DOMINANT_CANCEL_CONF and fan_prob <= DRYER_DOMINANT_CANCEL_FAN_PROB_MAX:
            self.dryer_dominant_fan_false_hits += 1
        else:
            self.dryer_dominant_fan_false_hits = max(0, self.dryer_dominant_fan_false_hits - 1)

        if self.dryer_dominant_fan_false_hits >= 2:
            removed_slots = []
            kept = []
            for item in self.active_devices:
                if item.get("device") == "fan":
                    removed_slots.append(int(item.get("slot", 0)))
                    if USE_DEVICE_SLOT_MEMORY:
                        self.device_slot_memory["fan"] = int(item.get("slot", 0))
                else:
                    kept.append(item)
            self.active_devices = kept

            # v17: 정말 false FAN으로 판단되어 제거하더라도 조용히 지우지 않고 FAN_OFF 잔상을 남긴다.
            # 이렇게 해야 사용자가 fan을 끈 상황과 UI 표현이 맞고, residual ghost re-add도 recent_off_memory로 막을 수 있다.
            for slot in removed_slots:
                self.off_events.append({
                    "device": "fan",
                    "slot": slot,
                    "hold": OFF_HOLD_BLOCKS,
                    "conf": max(fan_prob, 0.80),
                    "source": "dryer_dominant_stack_clear",
                })
                self.recent_off_devices["fan"] = RECENT_OFF_MEMORY_BLOCKS
                self.recovery_hits["fan"] = 0
                if USE_DEVICE_SLOT_MEMORY:
                    self.device_slot_memory["fan"] = slot

            self.dryer_dominant_fan_false_hits = 0
            if self.verbose:
                print(
                    f"[DELTA STACK] moved FAN to OFF while DRYER dominant | "
                    f"abs_conf={abs_conf:.2f}, fan_prob={fan_prob:.2f}, slots={[s+1 for s in removed_slots]}"
                )

    def _select_off_device(self, predicted_device, event):
        """
        OFF 이벤트에서 어떤 active device를 제거할지 선택.
        1순위: delta classifier가 예측한 device가 active에 있으면 그걸 제거.
        2순위: active가 하나뿐이면 그걸 제거.
        3순위: ON 당시 signature와 OFF delta 크기가 가장 가까운 device 제거.
        """
        active_names = [x["device"] for x in self.active_devices]

        # v24: COOKER_ON + 잘못 추가된 DRYER_ON 상태에서 값이 cooker standby/off 영역으로 내려오면
        # 실제로는 cooker heating이 꺼진 것이다. 이때 DRYER가 아니라 COOKER_OFF를 우선한다.
        latest = self.latest_features or {}
        new_mean = event.get("new_mean", {}) if event else {}
        if "cooker" in active_names and _is_cooker_standby_off_features(latest):
            return "cooker"
        if "cooker" in active_names and _is_cooker_standby_off_features(new_mean):
            return "cooker"

        # v20: DRYER_ON + FAN_ON 상태에서 드라이기만 꺼지면 전체 feature가 fan 단독 영역으로 내려간다.
        # 기존 v18 fan-off 우선 규칙은 이 큰 음수 delta를 "fan OFF"로 먼저 골라서,
        # 이후 _should_cancel_fan_off()가 fan still alive로 취소하며 DRYER_ON이 계속 남았다.
        # 따라서 현재 latest/new_mean이 fan alive이고 dryer alive가 아니면 DRYER_OFF를 우선 선택한다.
        latest = self.latest_features or {}
        new_mean = event.get("new_mean", {}) if event else {}
        if "fan" in active_names and "dryer" in active_names:
            latest_fan_only = _is_fan_alive_features(latest) and not _is_dryer_alive_features(latest)
            new_mean_fan_only = _is_fan_alive_features(new_mean) and not _is_dryer_alive_features(new_mean)
            if latest_fan_only or new_mean_fan_only:
                if self.verbose:
                    p = _safe_float(latest.get("Pabs_mean_proxy", 0.0))
                    i = _safe_float(latest.get("Irms_adc", 0.0))
                    h1 = _safe_float(latest.get("H1_60_mag", 0.0))
                    print(
                        "[DELTA SELECT] OFF -> DRYER: fan-only state remains after drop | "
                        f"I={i:.2f}, Pabs={p:.1f}, H1={h1:.1f}"
                    )
                return "dryer"

        # v18: DRYER_ON + FAN_ON 상태에서 fan을 끄면 device 모델이 dryer로 흔들리거나
        # dryer 모드 변화로 보일 수 있다. 그래도 OFF delta 크기가 fan 1대 크기이고,
        # active FAN이 너무 방금 켜진 상태가 아니면 FAN_OFF를 우선한다.
        if "fan" in active_names and "dryer" in active_names and _is_fan_off_sized_with_dryer_event(event):
            fan_items = [x for x in self.active_devices if x.get("device") == "fan"]
            fan_age = max([int(x.get("age", 0)) for x in fan_items] or [0])
            if fan_age >= FAN_OFF_GRACE_BLOCKS:
                return "fan"

        if predicted_device in active_names:
            return predicted_device

        if len(self.active_devices) == 1:
            return self.active_devices[0]["device"]

        off_sig = self._signature_from_event(event, use_abs=True)

        best = None
        best_score = None

        for item in self.active_devices:
            sig = item.get("signature", {})
            score = 0.0
            for key, weight in [("Pabs_mean_proxy", 1.0), ("Irms_adc", 0.6), ("H1_60_mag", 0.8)]:
                a = _safe_float(sig.get(key, 0.0))
                b = _safe_float(off_sig.get(key, 0.0))
                denom = max(abs(a), abs(b), 1.0)
                score += weight * abs(a - b) / denom

            if best_score is None or score < best_score:
                best_score = score
                best = item["device"]

        return best

    def _signature_from_latest(self, latest):
        """absolute_sync처럼 이벤트 없이 추가된 기기의 대표 feature를 저장한다."""
        latest = latest or {}
        return {
            "Pabs_mean_proxy": _safe_float(latest.get("Pabs_mean_proxy", 0.0)),
            "Irms_adc": _safe_float(latest.get("Irms_adc", 0.0)),
            "H1_60_mag": _safe_float(latest.get("H1_60_mag", 0.0)),
            "THD_i": _safe_float(latest.get("THD_i", 0.0)),
        }

    def _signature_from_event(self, event, use_abs=False):
        delta = event.get("delta", {})
        sig = {}
        for key in ["Pabs_mean_proxy", "Irms_adc", "H1_60_mag", "THD_i"]:
            v = _safe_float(delta.get(key, 0.0))
            sig[key] = abs(v) if use_abs else max(0.0, v)
        return sig

    def _slot_for_device(self, device):
        """같은 기기는 가능한 한 예전에 쓰던 표시 slot을 재사용한다.

        v13: OFF 잔상 시간이 끝나도 retained_off_slots에 slot 정보를 보존한다.
        같은 기기가 다시 켜지면 그 slot을 우선 재사용한다.
        """
        device = _normalize_device_name(device)
        used_active = set([int(x.get("slot", 0)) for x in self.active_devices])

        # 같은 기기의 OFF 잔상이 있으면 그 slot을 최우선으로 재사용
        for item in self.off_events:
            if item.get("device") == device:
                slot = int(item.get("slot", 0))
                if slot not in used_active:
                    return slot

        # v13: hold가 끝난 OFF memory도 같은 기기면 재사용
        for slot, info in list(self.retained_off_slots.items()):
            if info.get("device") == device and int(slot) not in used_active:
                return int(slot)

        if USE_DEVICE_SLOT_MEMORY and device in self.device_slot_memory:
            slot = int(self.device_slot_memory[device])
            # retained_off_slots가 같은 기기라면 used로 보지 않고 재사용한다.
            retained = self.retained_off_slots.get(slot)
            if slot not in used_active and (retained is None or retained.get("device") == device):
                return slot

        return self._first_free_slot()

    def _first_free_slot(self):
        used = set([int(x.get("slot", 0)) for x in self.active_devices])
        used.update([int(x.get("slot", 0)) for x in self.off_events])
        # v13: 식별된 후 OFF로 유지되는 slot도 다른 기기가 덮어쓰지 않게 예약한다.
        used.update([int(s) for s in self.retained_off_slots.keys()])
        for i in range(MAX_ACTIVE_DEVICES):
            if i not in used:
                return i
        return min(len(self.active_devices), MAX_ACTIVE_DEVICES - 1)

    def _remember_retained_off(self, item):
        """OFF hold가 끝난 뒤에도 slot의 마지막 기기 정보를 유지한다."""
        if not item:
            return
        dev = _normalize_device_name(item.get("device"))
        if dev is None:
            return
        slot = int(item.get("slot", 0))
        if not (0 <= slot < MAX_ACTIVE_DEVICES):
            return
        self.retained_off_slots[slot] = {
            "device": dev,
            "conf": _safe_float(item.get("conf", 0.80)),
            "source": item.get("source", "off_expired"),
        }
        if USE_DEVICE_SLOT_MEMORY:
            self.device_slot_memory[dev] = slot

    def _clear_retained_off(self, device=None, slot=None):
        """기기가 다시 ON 되면 같은 device/slot의 지속 OFF 표시를 제거한다."""
        device = _normalize_device_name(device) if device is not None else None
        remove_slots = []
        for s, info in list(self.retained_off_slots.items()):
            same_device = device is not None and info.get("device") == device
            same_slot = slot is not None and int(s) == int(slot)
            if same_device or same_slot:
                remove_slots.append(s)
        for s in remove_slots:
            self.retained_off_slots.pop(s, None)

    def _tick_off_events(self):
        new_items = []
        for item in self.off_events:
            item["hold"] = int(item.get("hold", 0)) - 1
            if item["hold"] > 0:
                new_items.append(item)
            else:
                # v13: OFF 잔상 시간이 끝나면 EMPTY로 지우지 말고 *_OFF를 persistent memory로 넘긴다.
                self._remember_retained_off(item)
        self.off_events = deque(new_items, maxlen=MAX_ACTIVE_DEVICES)

    def _is_idle_like_baseline(self, latest):
        if self.idle_baseline is None:
            return False

        p = _safe_float(latest.get("Pabs_mean_proxy", 0.0))
        i = _safe_float(latest.get("Irms_adc", 0.0))
        h1 = _safe_float(latest.get("H1_60_mag", 0.0))

        bp = _safe_float(self.idle_baseline.get("Pabs_mean_proxy", 0.0))
        bi = _safe_float(self.idle_baseline.get("Irms_adc", 0.0))
        bh1 = _safe_float(self.idle_baseline.get("H1_60_mag", 0.0))

        return (
            p <= bp + IDLE_MARGIN_PABS and
            i <= bi + IDLE_MARGIN_IRMS and
            h1 <= bh1 + IDLE_MARGIN_H1
        )

    def _make_output(self, ai_result, event=None):
        states = ["EMPTY"] * MAX_ACTIVE_DEVICES

        # active ON 기기 먼저 표시
        for item in self.active_devices:
            slot = int(item.get("slot", 0))
            if 0 <= slot < MAX_ACTIVE_DEVICES:
                states[slot] = f"{item['device'].upper()}_ON"

        active_device_names = {str(item.get("device", "")).lower() for item in self.active_devices}

        # OFF 잔상 표시. active가 이미 있는 슬롯이면 active 우선.
        # v18: 같은 기기가 다른 slot에서 ON인 경우, 이전 FAN_OFF/DRYER_OFF 잔상은 표시하지 않는다.
        for item in self.off_events:
            slot = int(item.get("slot", 0))
            dev = str(item.get("device", "")).lower()
            if dev in active_device_names:
                continue
            if 0 <= slot < MAX_ACTIVE_DEVICES and states[slot] == "EMPTY":
                states[slot] = f"{item['device'].upper()}_OFF"

        # v13: OFF hold가 끝난 뒤에도 식별된 slot은 계속 DEVICE_OFF로 유지한다.
        for slot, info in sorted(self.retained_off_slots.items()):
            slot = int(slot)
            dev = info.get("device")
            if str(dev).lower() in active_device_names:
                continue
            if dev and 0 <= slot < MAX_ACTIVE_DEVICES and states[slot] == "EMPTY":
                states[slot] = f"{str(dev).upper()}_OFF"

        # 아무 active/off도 없을 때 표시 보정
        if all(s == "EMPTY" for s in states):
            latest = None
            if ai_result:
                latest = ai_result.get("block_features") or self._result_to_minimal_features(ai_result)

            global_state = str(ai_result.get("state", "empty")).lower() if ai_result else "empty"

            # 시작 직후 아무 기기도 켠 적이 없으면 plugged_off보다 EMPTY를 우선한다.
            if global_state in ["plugged_off", "off", "standby", "idle"]:
                if latest is not None and self._is_idle_like_baseline(latest):
                    pass  # EMPTY 유지
                else:
                    # 이전에 감지된 기기가 전혀 없으면 유령 plugged_off 방지 차원에서 EMPTY 유지
                    # 실제 '꽂혀 있지만 꺼짐'까지 구분하려면 대기전력 학습 또는 소켓별 센서가 필요하다.
                    pass

        active_texts = [s for s in states if s != "EMPTY"]
        ai_text = f"🤖 AI: {' + '.join(active_texts)}" if active_texts else "🤖 AI: EMPTY"

        return {
            "socket_states": states,
            "ai_text": ai_text,
            "active_devices": list(self.active_devices),
            "off_events": list(self.off_events),
            "retained_off_slots": dict(self.retained_off_slots),
            "event": event,
        }


class AIEngine(DSPEngine if DSPEngine is not None else object):
    """
    기존 dashboard/main.py 호환용 AIEngine.

    변경된 역할:
    - DSPEngine.process_raw_mode()로 전체 ch0/ch1/fs_actual을 받는다.
    - NILMAIExtension으로 기존 전체 state/device 예측을 수행한다.
    - DeltaMultiDeviceTracker로 ON/OFF 변화량 이벤트를 감지한다.
    - active_devices 리스트를 유지해서 여러 기기를 동시에 UI에 표시한다.
    """

    def __init__(self, spi_core, buffer_size=150, verbose=True):
        if DSPEngine is None:
            raise ImportError(f"DSPEngine/DashboardUI import 실패: {_ADAPTER_IMPORT_ERROR}")

        super().__init__(spi_core, buffer_size)

        self.ai = NILMAIExtension(verbose=verbose)
        self.tracker = DeltaMultiDeviceTracker(self.ai, verbose=verbose)

        self.ai_text = "🤖 AI: READY"
        self.socket_states = ["EMPTY", "EMPTY", "EMPTY", "EMPTY"]

    def process_raw_mode(self, *args, **kwargs):
        ret = super().process_raw_mode(*args, **kwargs)

        if ret is None or len(ret) < 4:
            return ret

        ch0, ch1, timestamps, fs_actual = ret[:4]

        try:
            result = self.ai.process_samples(ch0, ch1, fs_actual)
            self._apply_ai_result(result)
        except Exception as e:
            print(f"[AI ADAPTER ERROR] {e}")
            self.ai_text = "🤖 AI: ERROR"
            self.socket_states = ["EMPTY", "EMPTY", "EMPTY", "EMPTY"]

        return ret

    def _apply_ai_result(self, result):
        if not result or not result.get("ready", False):
            self.ai_text = "🤖 AI: READY"
            self.socket_states = ["EMPTY", "EMPTY", "EMPTY", "EMPTY"]
            return

        tracker_out = self.tracker.update(result)

        self.socket_states = tracker_out["socket_states"][:4]
        self.ai_text = tracker_out["ai_text"]

        state = str(result.get("state", "empty")).lower()
        raw_state = str(result.get("raw_state", state)).lower()
        state_conf = _safe_float(result.get("state_conf", 0.0))
        abs_device = _normalize_device_name(result.get("device", None))
        device_conf = _safe_float(result.get("device_conf", 0.0))

        event = tracker_out.get("event")
        event_text = "None"
        if event is not None:
            event_text = event.get("type", "?").upper()

        print(
            f"[AI ADAPTER] state={state} raw={raw_state} "
            f"sconf={state_conf:.2f} abs_device={abs_device} dconf={device_conf:.2f} "
            f"event={event_text} active={self.socket_states} display={self.ai_text}"
        )


class AIDashboardUI(DashboardUI if DashboardUI is not None else object):
    """
    기존 dashboard_ui 위에 소켓 상태 텍스트만 추가하는 UI wrapper.
    """

    def __init__(self, *args, **kwargs):
        if DashboardUI is None:
            raise ImportError(f"DSPEngine/DashboardUI import 실패: {_ADAPTER_IMPORT_ERROR}")

        super().__init__(*args, **kwargs)

        self.fig.subplots_adjust(left=0.3)

        self.fig.text(
            0.03,
            0.9,
            "AI MULTITAP",
            color="cyan",
            fontsize=18,
            fontweight="bold",
        )

        self.socket_texts = []

        for i in range(4):
            txt = self.fig.text(
                0.03,
                0.7 - (i * 0.18),
                f"[ Slot {i + 1} ]\nEMPTY",
                color="gray",
                fontsize=15,
                fontweight="bold",
            )
            self.socket_texts.append(txt)

    def update_frame(self, frame):
        artists = super().update_frame(frame)

        if hasattr(self, "engine") and hasattr(self.engine, "socket_states"):
            for i in range(4):
                state = self.engine.socket_states[i]

                if state == "EMPTY":
                    color = "gray"
                elif "OFF" in state or state == "PLUGGED_OFF":
                    color = "orange"
                else:
                    color = "lime"

                self.socket_texts[i].set_text(f"[ Slot {i + 1} ]\n{state}")
                self.socket_texts[i].set_color(color)

                if isinstance(artists, list):
                    artists.append(self.socket_texts[i])

        if hasattr(self, "ax1") and hasattr(self, "engine") and hasattr(self.engine, "ai_text"):
            curr_title = self.ax1.get_title().split("  ||  ")[0]
            self.ax1.set_title(f"{curr_title}  ||  {self.engine.ai_text}", color="yellow")

        return artists


# =========================================================
# 8. 단독 실행 테스트용
# =========================================================

if __name__ == "__main__":
    """
    단독 실행 시 모델 로드만 테스트.
    실시간 SPI 테스트는 main 수집/실행 코드에서 process_samples()를 호출해야 함.
    """
    ai = NILMAIExtension(verbose=True)

    print("\n[TEST] 모델 로드 성공")
    print("[TEST] 이 파일은 단독 실행 시 SPI를 읽지 않습니다.")
    print("[TEST] 실시간 코드에서 process_samples(ch0_block, ch1_block, fs)를 호출하세요.")