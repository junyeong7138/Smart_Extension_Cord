#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_extension.py - clean NILM realtime extension

Clean version after v18; v30 cooker OFF start guard + dryer false-positive block:
- Uses RF state/device models directly. Device classes can include charger/cooker/dryer/fan.
- Keeps only the practical logic that has been useful in tests:
  1) feature extraction
  2) state/device prediction
  3) delta-based active-device stack
  4) persistent OFF slot memory
  5) fan protection while dryer mode changes
  6) model-based cooker support

main.py compatibility:
    from ai_extension import AIEngine, AIDashboardUI
"""

import os
import json
import time
from collections import deque

import joblib
import numpy as np
import pandas as pd

AI_VERSION = "ai_extension_2026_05_19_v31_cooker_off_start_owns_pulse"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EPS = 1e-9


# =========================================================
# Model path
# =========================================================

def find_model_dir():
    cwd = os.getcwd()
    candidates = [
        os.path.join(BASE_DIR, "Model"),
        os.path.join(BASE_DIR, "..", "Model"),
        os.path.join(BASE_DIR, "..", "..", "Model"),
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
    for p in checked:
        print("  -", p)
    return os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Model"))


MODEL_DIR = find_model_dir()
STATE_MODEL_PATH = os.path.join(MODEL_DIR, "rf_state_classifier.joblib")
STATE_FEATURE_INFO_PATH = os.path.join(MODEL_DIR, "rf_state_features.json")
DEVICE_MODEL_PATH = os.path.join(MODEL_DIR, "rf_device_classifier.joblib")
DEVICE_FEATURE_INFO_PATH = os.path.join(MODEL_DIR, "rf_device_features.json")


# =========================================================
# Feature settings
# =========================================================

WINDOW_SIZE_DEFAULT = 10
USE_PERCENTILE_CLIP = True
CLIP_LOW_PCT = 1
CLIP_HIGH_PCT = 99
STATE_SMOOTH_N = 3
DEVICE_SMOOTH_N = 3
STATE_ON_MIN_CONF = 0.45
DEVICE_MIN_CONF = 0.40
MIN_PRINT_INTERVAL_SEC = 0.3

BASE_FEATURE_COLS = [
    "Vrms_adc", "Irms_adc", "Vpeak_adc", "Ipeak_adc", "Vpp_adc", "Ipp_adc",
    "Iabs_mean_adc", "Istd_adc", "crest_factor_i",
    "P_proxy", "Pabs_mean_proxy", "Ppeak_proxy", "Pstd_proxy",
    "H1_60_mag", "H3_180_mag", "H5_300_mag", "H7_420_mag",
    "THD_i", "H3_ratio", "H5_ratio", "H7_ratio",
    "fft_peak_freq", "fft_peak_mag",
]


# =========================================================
# Tracker thresholds
# =========================================================

MAX_SLOTS = 4
DELTA_OLD_N = 6
DELTA_NEW_N = 3
DELTA_HISTORY_N = DELTA_OLD_N + DELTA_NEW_N + 5
OFF_HOLD_BLOCKS = 18

ON_DELTA_PABS_MIN = 4500.0
ON_DELTA_IRMS_MIN = 8.0
ON_DELTA_H1_MIN = 250.0
EVENT_SCORE_MIN = 2
EVENT_COOLDOWN_BLOCKS = 5

IDLE_PABS_MAX = 4500.0
IDLE_IRMS_MAX = 8.0
IDLE_H1_MAX = 180.0
IDLE_CLEAR_HITS_REQUIRED = 2

FAN_ALIVE_PABS_MIN = 6500.0
FAN_ALIVE_PABS_MAX = 30000.0
FAN_ALIVE_IRMS_MIN = 12.0
FAN_ALIVE_IRMS_MAX = 55.0
FAN_ALIVE_H1_MIN = 450.0
FAN_ALIVE_H1_MAX = 2500.0

DRYER_ALIVE_PABS_MIN = 30000.0
DRYER_ALIVE_IRMS_MIN = 55.0
DRYER_ALIVE_H1_MIN = 2500.0
DRYER_FAST_PABS_MIN = 45000.0
DRYER_FAST_IRMS_MIN = 70.0
DRYER_FAST_H1_MIN = 3000.0
DRYER_FAST_HITS_REQUIRED = 2
DRYER_STRONG_PABS_MIN = 90000.0
DRYER_STRONG_IRMS_MIN = 150.0
DRYER_STRONG_H1_MIN = 9000.0

# v22: dryer and cooker overlap heavily in RF probabilities.
# Use physical ranges + THD/probability plausibility instead of broad single ranges.
DRYER_LOW_PABS_MIN = 28000.0
DRYER_LOW_IRMS_MIN = 50.0
DRYER_LOW_H1_MIN = 2200.0

# Dryer ramp guard: prevents the first dryer slow_low step from being accepted as FAN_ON.
DRYER_RAMP_PABS_MIN = 26000.0
DRYER_RAMP_IRMS_MIN = 45.0
DRYER_RAMP_H1_MIN = 1800.0

# Cooker profile has two practical regions observed after adding cooker model:
# - low cooker: overlaps with fan in P/I/H1, but has noticeably higher THD
# - mid cooker: requires RF cooker confidence; otherwise dryer slow/mid wins
# v23: cooker-only logs show real cooker steady around
# I=18~25, Pabs=7.5k~11.5k, H1=850~1200, THD=0.18~0.37.
# v22 rejected this as weak/implausible or kept converting it to FAN/DRYER.
COOKER_LOW_PABS_MIN = 6500.0
COOKER_LOW_PABS_MAX = 18000.0
COOKER_LOW_IRMS_MIN = 16.0
COOKER_LOW_IRMS_MAX = 42.0
COOKER_LOW_H1_MIN = 300.0
COOKER_LOW_H1_MAX = 1700.0
COOKER_LOW_THD_MIN = 0.140
COOKER_LOW_THD_MAX = 0.55

COOKER_MID_PABS_MIN = 26000.0
COOKER_MID_PABS_MAX = 95000.0
COOKER_MID_IRMS_MIN = 40.0
COOKER_MID_IRMS_MAX = 170.0
COOKER_MID_H1_MIN = 1800.0
COOKER_MID_H1_MAX = 8500.0
# Dryer slow/mid has usually low THD in the logs, while cooker heating/ramp
# showed THD around 0.10~0.13 or higher. Use this to keep cooker from becoming dryer.
COOKER_MID_THD_MIN = 0.060
COOKER_MID_THD_STRONG_MIN = 0.100
COOKER_MID_THD_MAX = 0.40

COOKER_PROB_STRONG = 0.65
COOKER_PROB_MARGIN = 0.25


# If dryer is already active, a fan ON delta can be small or partially buried.
FAN_WITH_DRYER_I_MIN = 5.0
FAN_WITH_DRYER_I_MAX = 55.0
FAN_WITH_DRYER_H1_MIN = 250.0
FAN_WITH_DRYER_H1_MAX = 3800.0
FAN_WITH_DRYER_PABS_ABS_MAX = 35000.0

# Dryer baseline residual for fan OFF while dryer remains ON.
FAN_RESIDUAL_PABS_MIN = 1800.0
FAN_RESIDUAL_PABS_MAX = 30000.0
FAN_RESIDUAL_IRMS_MIN = 3.8
FAN_RESIDUAL_IRMS_MAX = 55.0
FAN_RESIDUAL_H1_MIN = 150.0
FAN_RESIDUAL_H1_MAX = 3200.0
FAN_MISSING_PABS_MAX = 2500.0
FAN_MISSING_IRMS_MAX = 5.0
FAN_MISSING_H1_MAX = 300.0
FAN_MISSING_HITS_REQUIRED = 4
MODE_TRANSITION_PABS = 12000.0
MODE_TRANSITION_IRMS = 18.0
MODE_TRANSITION_H1 = 900.0

# Absolute sync thresholds.
ABS_SYNC_HITS_REQUIRED = 2
FAN_ABS_CONF_MIN = 0.88
FAN_ABS_ON_PROB_MIN = 0.70
CHARGER_ABS_CONF_MIN = 0.82
CHARGER_ABS_ON_PROB_MIN = 0.70
COOKER_ABS_CONF_MIN = 0.55
COOKER_ABS_ON_PROB_MIN = 0.50

# Delta model confidence thresholds.
DELTA_DEVICE_MIN_CONF = 0.35
CHARGER_DELTA_CONF_MIN = 0.78
COOKER_DELTA_CONF_MIN = 0.50

# v24 cooker lock: cooker often starts in a low/THD-rich region and later ramps
# into dryer-like power. Once low cooker is confirmed, keep cooker ownership
# through ramp/heating blocks until the signal becomes idle.
COOKER_LOCK_BLOCKS = 80
COOKER_LOCK_CONF = 0.76
COOKER_LOW_CONFIRM_HITS_REQUIRED = 3

# v26: distinguish rice-cooker plugged/standby load from real cooking/heating ON.
# In the logs, cooker plug/standby can look like the old low cooker signature:
# I≈18~24, Pabs≈7k~11k, H1≈800~1100, THD≈0.18~0.35 while raw_state is still
# plugged_off and on_prob is low.  Treat that as COOKER_OFF until a real ON
# signal appears.
COOKER_PLUG_ON_PROB_MAX = 0.55
COOKER_STANDBY_HITS_REQUIRED = 2
COOKER_OFF_HITS_TO_REMOVE_ACTIVE = 4
# v27: low cooker-like standby often fools the state model.
# Only accept the low cooker region as real ON when state ON is very strong.
COOKER_RUN_ON_PROB_MIN = 0.88
COOKER_RUN_RAMP_PABS_MIN = 18000.0
COOKER_RUN_RAMP_IRMS_MIN = 35.0
COOKER_RUN_RAMP_H1_MIN = 1500.0
COOKER_RUN_RAMP_THD_MIN = 0.055

# v25: cooker lock should protect cooker itself, but it must not swallow a
# real dryer that is turned on later.  We therefore require a separate,
# persistent dryer signature before adding DRYER_ON while COOKER_ON is locked.
COOKER_WITH_DRYER_HITS_REQUIRED = 5
# v29: cooker-only heating can briefly look dryer-like.  Require dryer RF
# probability to be truly dominant before adding a separate DRYER_ON under COOKER_ON.
COOKER_DRYER_PROB_MIN = 0.72
COOKER_DRYER_PROB_MARGIN = 0.20
COOKER_DRYER_LOW_PABS_MIN = 38000.0
COOKER_DRYER_LOW_IRMS_MIN = 60.0
COOKER_DRYER_LOW_H1_MIN = 2800.0
COOKER_DRYER_LOW_THD_MAX = 0.13
COOKER_DRYER_STRONG_PABS_MIN = 90000.0
COOKER_DRYER_STRONG_IRMS_MIN = 150.0
COOKER_DRYER_STRONG_H1_MIN = 8000.0
COOKER_DRYER_STRONG_THD_MAX = 0.10
# v27: absolute dryer override under cooker lock. When cooker is active, a real
# dryer can dominate P/I/H1 while RF probabilities still prefer cooker because
# the 10-block window contains cooker history. These thresholds let a physically
# undeniable dryer be added even when cooker_prob is stale-high.
COOKER_DRYER_PHYS_OVERRIDE_PABS_MIN = 120000.0
COOKER_DRYER_PHYS_OVERRIDE_IRMS_MIN = 220.0
COOKER_DRYER_PHYS_OVERRIDE_H1_MIN = 10000.0
COOKER_DRYER_PHYS_OVERRIDE_THD_MAX = 0.075
# v29: after COOKER_ON, long low/standby-like period with no heating pulse
# should return to COOKER_OFF.  The hold prevents normal cooker duty cycling
# from being misread as OFF immediately after a heating pulse.
COOKER_HEAT_HOLD_BLOCKS = 6
COOKER_LOW_OFF_HITS_REQUIRED = 6
COOKER_LOW_AFTER_ON_PABS_MAX = 15000.0
COOKER_LOW_AFTER_ON_IRMS_MAX = 35.0
COOKER_LOW_AFTER_ON_H1_MAX = 1500.0
COOKER_HIGH_ACTIVITY_PABS_MIN = 25000.0
COOKER_HIGH_ACTIVITY_IRMS_MIN = 40.0
COOKER_HIGH_ACTIVITY_H1_MIN = 1700.0
# v30: when a rice cooker is already retained as COOKER_OFF, the first large
# heating pulse must promote that same cooker to COOKER_ON, not become DRYER_ON.
COOKER_OFF_START_PABS_MIN = 18000.0
COOKER_OFF_START_IRMS_MIN = 35.0
COOKER_OFF_START_H1_MIN = 1500.0
COOKER_OFF_START_THD_MIN = 0.000  # v31: cooker heater start can be low-THD like dryer
COOKER_OFF_START_COOKER_PROB_MIN = 0.30
COOKER_OFF_START_DRYER_MARGIN_MAX = 0.35
COOKER_OFF_START_DRYER_HARD_PROB_MIN = 0.70
COOKER_OFF_START_DRYER_HARD_MARGIN = 0.25
COOKER_DRYER_ULTRA_PABS_MIN = 500000.0
COOKER_DRYER_ULTRA_IRMS_MIN = 850.0
COOKER_DRYER_ULTRA_H1_MIN = 42000.0
COOKER_DRYER_ULTRA_THD_MAX = 0.080


# =========================================================
# Basic utilities
# =========================================================

def safe_float(x, default=0.0):
    try:
        v = float(x)
        if np.isnan(v) or np.isinf(v):
            return default
        return v
    except Exception:
        return default


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_device(device):
    if device is None:
        return None
    d = str(device).strip().lower().replace("_on", "").replace("_off", "")
    if d in ["", "none", "unknown", "unknown_on", "nan"]:
        return None
    return d


def format_prob_dict(prob_dict, topk=4):
    if not prob_dict:
        return ""
    items = sorted(prob_dict.items(), key=lambda kv: kv[1], reverse=True)[:topk]
    return ", ".join([f"{k}={v:.2f}" for k, v in items])


def majority_vote(items):
    if not items:
        return None
    counts = {}
    for x in items:
        counts[x] = counts.get(x, 0) + 1
    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[0][0]


def predict_with_proba(model, X, labels_from_json=None):
    pred = model.predict(X)[0]
    prob_dict = {}
    conf = 1.0
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        prob_dict = {str(c): float(p) for c, p in zip(list(model.classes_), proba)}
        conf = float(prob_dict.get(str(pred), 0.0))
    if labels_from_json is not None:
        for label in labels_from_json:
            prob_dict.setdefault(str(label), 0.0)
    return str(pred), conf, prob_dict


def triplet(row):
    return {
        "Pabs_mean_proxy": safe_float(row.get("Pabs_mean_proxy", 0.0)),
        "Irms_adc": safe_float(row.get("Irms_adc", 0.0)),
        "H1_60_mag": safe_float(row.get("H1_60_mag", 0.0)),
    }


def sub_triplet(a, b):
    return {
        "Pabs_mean_proxy": safe_float(a.get("Pabs_mean_proxy", 0.0)) - safe_float(b.get("Pabs_mean_proxy", 0.0)),
        "Irms_adc": safe_float(a.get("Irms_adc", 0.0)) - safe_float(b.get("Irms_adc", 0.0)),
        "H1_60_mag": safe_float(a.get("H1_60_mag", 0.0)) - safe_float(b.get("H1_60_mag", 0.0)),
    }


def abs_triplet(row):
    t = triplet(row)
    return {k: abs(v) for k, v in t.items()}


def score_axes(row, p_min, i_min, h_min):
    t = abs_triplet(row)
    return int(t["Pabs_mean_proxy"] >= p_min) + int(t["Irms_adc"] >= i_min) + int(t["H1_60_mag"] >= h_min)


def is_idle(row):
    t = triplet(row)
    return t["Pabs_mean_proxy"] <= IDLE_PABS_MAX and t["Irms_adc"] <= IDLE_IRMS_MAX and t["H1_60_mag"] <= IDLE_H1_MAX


def is_fan_alive(row):
    t = triplet(row)
    return (
        FAN_ALIVE_PABS_MIN <= t["Pabs_mean_proxy"] <= FAN_ALIVE_PABS_MAX and
        FAN_ALIVE_IRMS_MIN <= t["Irms_adc"] <= FAN_ALIVE_IRMS_MAX and
        FAN_ALIVE_H1_MIN <= t["H1_60_mag"] <= FAN_ALIVE_H1_MAX
    )


def is_dryer_alive(row):
    return score_axes(row, DRYER_ALIVE_PABS_MIN, DRYER_ALIVE_IRMS_MIN, DRYER_ALIVE_H1_MIN) >= 2


def is_dryer_fast(row):
    return score_axes(row, DRYER_FAST_PABS_MIN, DRYER_FAST_IRMS_MIN, DRYER_FAST_H1_MIN) >= 2


def is_dryer_profile(row):
    """Physical dryer guard including slow_low / middle / high modes."""
    return score_axes(row, DRYER_LOW_PABS_MIN, DRYER_LOW_IRMS_MIN, DRYER_LOW_H1_MIN) >= 2


def is_dryer_ramp_like(row):
    """Early dryer ramp can have fan-sized delta but dryer-sized absolute level."""
    return score_axes(row, DRYER_RAMP_PABS_MIN, DRYER_RAMP_IRMS_MIN, DRYER_RAMP_H1_MIN) >= 2


def is_strong_dryer(row):
    return score_axes(row, DRYER_STRONG_PABS_MIN, DRYER_STRONG_IRMS_MIN, DRYER_STRONG_H1_MIN) >= 2


def is_cooker_low_profile(row):
    t = triplet(row)
    thd = safe_float(row.get("THD_i", 0.0))
    return (
        COOKER_LOW_PABS_MIN <= t["Pabs_mean_proxy"] <= COOKER_LOW_PABS_MAX and
        COOKER_LOW_IRMS_MIN <= t["Irms_adc"] <= COOKER_LOW_IRMS_MAX and
        COOKER_LOW_H1_MIN <= t["H1_60_mag"] <= COOKER_LOW_H1_MAX and
        COOKER_LOW_THD_MIN <= thd <= COOKER_LOW_THD_MAX
    )


def is_cooker_plug_standby(row, state_probs=None, raw_state=None):
    """Rice cooker is connected but not actually running.

    This is intentionally conservative: only low cooker-like load + raw plugged_off
    + low on_prob becomes COOKER_OFF.  Once raw/on probability becomes stronger or
    the load ramps upward, the normal cooker ON/ramp logic can take over.
    """
    if not is_cooker_low_profile(row):
        return False
    state_probs = state_probs or {}
    onp = safe_float(state_probs.get("on", 0.0))
    raw = str(raw_state or "").lower()
    return raw in {"plugged_off", "empty"} and onp <= COOKER_PLUG_ON_PROB_MAX


def is_cooker_running_signal(row, state_probs=None, raw_state=None, probs=None):
    """Evidence that cooker is actually heating/running, not just plugged."""
    state_probs = state_probs or {}
    onp = safe_float(state_probs.get("on", 0.0))
    raw = str(raw_state or "").lower()
    thd = safe_float(row.get("THD_i", 0.0))

    # v28: low cooker/standby region alone is NOT enough to become COOKER_ON.
    # Rice cooker plug/keep-warm/idle can make raw_state flip to on around 0.6~0.75
    # without actual cooking.  Accept low region only with very strong state AND
    # actual cooker probability; otherwise keep COOKER_OFF until a ramp/heating block.
    cooker_p = safe_float((probs or {}).get("cooker", 0.0))
    if is_cooker_low_profile(row) and onp >= COOKER_RUN_ON_PROB_MIN and cooker_p >= 0.70:
        return True

    # Heating/ramp region: larger P/I/H1 with some cooker-like harmonic content.
    ramp_axes = score_axes(row, COOKER_RUN_RAMP_PABS_MIN, COOKER_RUN_RAMP_IRMS_MIN, COOKER_RUN_RAMP_H1_MIN)
    if ramp_axes >= 2 and thd >= COOKER_RUN_RAMP_THD_MIN and (raw == "on" or onp >= 0.50):
        return True

    # Existing mid cooker logic, but do not let raw plugged_off + low on_prob seed ON.
    if not is_cooker_plug_standby(row, state_probs, raw_state) and is_cooker_mid_profile(row, probs):
        return True

    return False


def is_cooker_start_from_off(row, probs=None):
    """Promote retained COOKER_OFF to COOKER_ON.

    v31 핵심:
    밥통은 플러그만 꽂힌 상태에서는 COOKER_OFF로 있다가, 취사를 시작하는
    첫 히터 펄스가 드라이어처럼 매우 큰 P/I/H1과 낮은 THD를 만들 수 있다.
    그래서 COOKER_OFF가 이미 기억된 상태라면 첫 큰 상승은 기본적으로
    밥통의 취사 시작으로 소유권을 준다. 단, RF가 압도적으로 dryer라고
    말할 때만 별도 DRYER_ON 후보로 넘긴다.
    """
    probs = probs or {}
    t = abs_triplet(row)
    thd = safe_float(row.get("THD_i", 0.0))
    ramp_axes = (
        int(t["Pabs_mean_proxy"] >= COOKER_OFF_START_PABS_MIN) +
        int(t["Irms_adc"] >= COOKER_OFF_START_IRMS_MIN) +
        int(t["H1_60_mag"] >= COOKER_OFF_START_H1_MIN)
    )
    if ramp_axes < 2:
        return False

    cooker_p = safe_float(probs.get("cooker", 0.0))
    dryer_p = safe_float(probs.get("dryer", 0.0))

    # If the device model did not run yet, do NOT let the delta model guess dryer.
    # The retained COOKER_OFF slot is stronger evidence for ownership.
    if not probs:
        return True

    # Only an overwhelming dryer RF win can steal this first pulse from the retained cooker.
    if dryer_p >= COOKER_OFF_START_DRYER_HARD_PROB_MIN and (dryer_p - cooker_p) >= COOKER_OFF_START_DRYER_HARD_MARGIN:
        return False

    # Low THD is no longer a rejection reason; cooker heater pulses are resistive too.
    if thd >= COOKER_OFF_START_THD_MIN:
        return cooker_p >= COOKER_OFF_START_COOKER_PROB_MIN or cooker_p >= (dryer_p - COOKER_OFF_START_DRYER_MARGIN_MAX)

    return False


def cooker_prob_strong(probs):
    probs = probs or {}
    cp = safe_float(probs.get("cooker", 0.0))
    rival = max(
        safe_float(probs.get("dryer", 0.0)),
        safe_float(probs.get("fan", 0.0)),
        safe_float(probs.get("charger", 0.0)),
    )
    return cp >= COOKER_PROB_STRONG and (cp - rival) >= COOKER_PROB_MARGIN


def is_cooker_mid_profile(row, probs=None):
    t = triplet(row)
    thd = safe_float(row.get("THD_i", 0.0))
    physical = (
        COOKER_MID_PABS_MIN <= t["Pabs_mean_proxy"] <= COOKER_MID_PABS_MAX and
        COOKER_MID_IRMS_MIN <= t["Irms_adc"] <= COOKER_MID_IRMS_MAX and
        COOKER_MID_H1_MIN <= t["H1_60_mag"] <= COOKER_MID_H1_MAX and
        COOKER_MID_THD_MIN <= thd <= COOKER_MID_THD_MAX
    )
    if not physical:
        return False
    # v23: if THD is clearly cooker-like, accept even when device_probs are not
    # available because the state model still says plugged_off during the ramp.
    if thd >= COOKER_MID_THD_STRONG_MIN:
        return True
    # Otherwise, in the overlap area, require RF cooker dominance.
    return cooker_prob_strong(probs)


def is_cooker_alive(row, probs=None):
    # v22: low cooker is THD-based; mid cooker needs both physical plausibility and RF dominance.
    return is_cooker_low_profile(row) or is_cooker_mid_profile(row, probs)


def is_cooker_lock_seed(row, probs=None):
    """Reliable entry pattern for cooker.

    Low cooker is the safest seed because it is THD-rich and usually appears
    before the heating/ramp phase. Mid cooker can also seed lock if THD is
    cooker-like or RF cooker probability is dominant.
    """
    if is_cooker_low_profile(row):
        return True
    if is_cooker_mid_profile(row, probs):
        return True
    return False


def is_cooker_ramp_under_lock(row):
    """Any non-idle, reasonably large load while cooker lock is active.

    Cooker heating can temporarily look like dryer in P/I/H1, so during lock we
    do not use dryer thresholds to steal ownership.
    """
    if is_idle(row):
        return False
    return score_axes(row, 6500.0, 16.0, 300.0) >= 2


def is_separate_dryer_candidate_under_cooker(row, probs=None, device=None, conf=0.0):
    """True only when a real dryer is likely added on top of a locked cooker.

    Cooker can ramp upward by itself, so high P/I/H1 alone is not enough.
    We require a dryer-like physical region *and* RF/device evidence that dryer
    is winning over cooker. This keeps cooker-only heating from being stolen,
    while allowing COOKER_ON + DRYER_ON when the dryer is actually switched on.
    """
    probs = probs or {}
    t = abs_triplet(row)
    thd = safe_float(row.get("THD_i", 0.0))
    dryer_prob = safe_float(probs.get("dryer", 0.0))
    cooker_prob = safe_float(probs.get("cooker", 0.0))

    dryer_low_phys = (
        t["Pabs_mean_proxy"] >= COOKER_DRYER_LOW_PABS_MIN and
        t["Irms_adc"] >= COOKER_DRYER_LOW_IRMS_MIN and
        t["H1_60_mag"] >= COOKER_DRYER_LOW_H1_MIN and
        thd <= COOKER_DRYER_LOW_THD_MAX
    )
    dryer_strong_phys = (
        t["Pabs_mean_proxy"] >= COOKER_DRYER_STRONG_PABS_MIN and
        t["Irms_adc"] >= COOKER_DRYER_STRONG_IRMS_MIN and
        t["H1_60_mag"] >= COOKER_DRYER_STRONG_H1_MIN and
        thd <= COOKER_DRYER_STRONG_THD_MAX
    )
    dryer_abs_override = (
        t["Pabs_mean_proxy"] >= COOKER_DRYER_PHYS_OVERRIDE_PABS_MIN and
        t["Irms_adc"] >= COOKER_DRYER_PHYS_OVERRIDE_IRMS_MIN and
        t["H1_60_mag"] >= COOKER_DRYER_PHYS_OVERRIDE_H1_MIN and
        thd <= COOKER_DRYER_PHYS_OVERRIDE_THD_MAX
    )
    dryer_ultra = (
        t["Pabs_mean_proxy"] >= COOKER_DRYER_ULTRA_PABS_MIN and
        t["Irms_adc"] >= COOKER_DRYER_ULTRA_IRMS_MIN and
        t["H1_60_mag"] >= COOKER_DRYER_ULTRA_H1_MIN and
        thd <= COOKER_DRYER_ULTRA_THD_MAX
    )
    if not (dryer_low_phys or dryer_strong_phys or dryer_abs_override or dryer_ultra):
        return False

    # v29: Cooker heating alone can produce P/I/H1 in dryer ranges.
    # Therefore physical magnitude alone is NOT enough.  Only accept a separate
    # dryer when the RF probability also turns clearly dryer-dominant.
    prob_win = (
        dryer_prob >= COOKER_DRYER_PROB_MIN and
        (dryer_prob - cooker_prob) >= COOKER_DRYER_PROB_MARGIN
    )
    model_win = (
        normalize_device(device) == "dryer" and
        safe_float(conf) >= 0.82 and
        dryer_prob >= COOKER_DRYER_PROB_MIN and
        (dryer_prob - cooker_prob) >= COOKER_DRYER_PROB_MARGIN
    )
    # Ultra-high region is allowed a little earlier, but still needs dryer to be
    # meaningfully competitive. This keeps cooker-only heater peaks from adding DRYER_ON.
    ultra_phys_win = (
        dryer_ultra and
        normalize_device(device) == "dryer" and
        dryer_prob >= 0.55 and
        dryer_prob >= cooker_prob
    )
    return prob_win or model_win or ultra_phys_win


def is_fan_like_delta(delta, dryer_active=False):
    d = triplet(delta)
    if dryer_active:
        return (
            abs(d["Pabs_mean_proxy"]) <= FAN_WITH_DRYER_PABS_ABS_MAX and
            FAN_WITH_DRYER_I_MIN <= d["Irms_adc"] <= FAN_WITH_DRYER_I_MAX and
            FAN_WITH_DRYER_H1_MIN <= d["H1_60_mag"] <= FAN_WITH_DRYER_H1_MAX
        )
    return (
        ON_DELTA_PABS_MIN <= d["Pabs_mean_proxy"] <= FAN_ALIVE_PABS_MAX and
        ON_DELTA_IRMS_MIN <= d["Irms_adc"] <= FAN_ALIVE_IRMS_MAX and
        ON_DELTA_H1_MIN <= d["H1_60_mag"] <= FAN_ALIVE_H1_MAX
    )


def is_fan_residual(res):
    r = triplet(res)
    return (
        FAN_RESIDUAL_PABS_MIN <= r["Pabs_mean_proxy"] <= FAN_RESIDUAL_PABS_MAX and
        FAN_RESIDUAL_IRMS_MIN <= r["Irms_adc"] <= FAN_RESIDUAL_IRMS_MAX and
        FAN_RESIDUAL_H1_MIN <= r["H1_60_mag"] <= FAN_RESIDUAL_H1_MAX
    )


def is_fan_missing_residual(res):
    r = triplet(res)
    return (
        abs(r["Pabs_mean_proxy"]) <= FAN_MISSING_PABS_MAX and
        abs(r["Irms_adc"]) <= FAN_MISSING_IRMS_MAX and
        abs(r["H1_60_mag"]) <= FAN_MISSING_H1_MAX
    )


def is_mode_transition_residual(res):
    r = triplet(res)
    return (
        abs(r["Pabs_mean_proxy"]) >= MODE_TRANSITION_PABS or
        abs(r["Irms_adc"]) >= MODE_TRANSITION_IRMS or
        abs(r["H1_60_mag"]) >= MODE_TRANSITION_H1
    )


# =========================================================
# Feature extraction
# =========================================================

def preprocess_block(x):
    x = np.asarray(x, dtype=np.float64)
    if len(x) == 0:
        return x
    if USE_PERCENTILE_CLIP:
        lo = np.percentile(x, CLIP_LOW_PCT)
        hi = np.percentile(x, CLIP_HIGH_PCT)
        if lo < hi:
            x = np.clip(x, lo, hi)
    return x - np.mean(x)


def compute_block_features(ch0_block, ch1_block, fs):
    c0 = preprocess_block(ch0_block)
    c1 = preprocess_block(ch1_block)

    vrms = float(np.sqrt(np.mean(c0 ** 2))) if len(c0) else 0.0
    irms = float(np.sqrt(np.mean(c1 ** 2))) if len(c1) else 0.0
    vpeak = float(np.max(np.abs(c0))) if len(c0) else 0.0
    ipeak = float(np.max(np.abs(c1))) if len(c1) else 0.0
    vpp = float(np.max(c0) - np.min(c0)) if len(c0) else 0.0
    ipp = float(np.max(c1) - np.min(c1)) if len(c1) else 0.0
    iabs_mean = float(np.mean(np.abs(c1))) if len(c1) else 0.0
    istd = float(np.std(c1)) if len(c1) else 0.0
    crest_factor_i = float(ipeak / irms) if irms > EPS else 0.0

    p_inst = c0 * c1
    p_proxy = float(np.mean(p_inst)) if len(p_inst) else 0.0
    pabs_mean_proxy = float(np.mean(np.abs(p_inst))) if len(p_inst) else 0.0
    ppeak_proxy = float(np.max(np.abs(p_inst))) if len(p_inst) else 0.0
    pstd_proxy = float(np.std(p_inst)) if len(p_inst) else 0.0

    h1 = h3 = h5 = h7 = thd = 0.0
    h3_ratio = h5_ratio = h7_ratio = 0.0
    fft_peak_freq = 0.0
    fft_peak_mag = 0.0

    if len(c1) > 16 and fs > 0:
        x = c1 - np.mean(c1)
        xw = x * np.hanning(len(x))
        mags = np.abs(np.fft.rfft(xw))
        freqs = np.fft.rfftfreq(len(xw), d=1.0 / fs)

        def mag_at(freq):
            idx = int(np.argmin(np.abs(freqs - freq)))
            return float(mags[idx])

        h1 = mag_at(60.0)
        h3 = mag_at(180.0)
        h5 = mag_at(300.0)
        h7 = mag_at(420.0)
        if h1 > EPS:
            thd = float(np.sqrt(h3 ** 2 + h5 ** 2 + h7 ** 2) / h1)
            h3_ratio = float(h3 / h1)
            h5_ratio = float(h5 / h1)
            h7_ratio = float(h7 / h1)

        valid = freqs >= 60.0
        if np.any(valid):
            vf = freqs[valid]
            vm = mags[valid]
            idx = int(np.argmax(vm))
            fft_peak_freq = float(vf[idx])
            fft_peak_mag = float(vm[idx])

    return {
        "Vrms_adc": vrms, "Irms_adc": irms,
        "Vpeak_adc": vpeak, "Ipeak_adc": ipeak,
        "Vpp_adc": vpp, "Ipp_adc": ipp,
        "Iabs_mean_adc": iabs_mean, "Istd_adc": istd, "crest_factor_i": crest_factor_i,
        "P_proxy": p_proxy, "Pabs_mean_proxy": pabs_mean_proxy,
        "Ppeak_proxy": ppeak_proxy, "Pstd_proxy": pstd_proxy,
        "H1_60_mag": h1, "H3_180_mag": h3,
        "H5_300_mag": h5, "H7_420_mag": h7,
        "THD_i": thd, "H3_ratio": h3_ratio,
        "H5_ratio": h5_ratio, "H7_ratio": h7_ratio,
        "fft_peak_freq": fft_peak_freq, "fft_peak_mag": fft_peak_mag,
    }


def make_window_features_from_blocks(block_rows, required_feature_names):
    df = pd.DataFrame(list(block_rows))
    feat = {}
    for col in BASE_FEATURE_COLS:
        values = pd.to_numeric(df[col], errors="coerce") if col in df.columns else pd.Series([], dtype=float)
        values = values.replace([np.inf, -np.inf], np.nan).dropna()
        feat[f"{col}_mean"] = float(values.mean()) if len(values) else 0.0
        feat[f"{col}_std"] = float(values.std(ddof=0)) if len(values) else 0.0
        feat[f"{col}_min"] = float(values.min()) if len(values) else 0.0
        feat[f"{col}_max"] = float(values.max()) if len(values) else 0.0
    row = {name: feat.get(name, 0.0) for name in required_feature_names}
    return pd.DataFrame([row], columns=required_feature_names).replace([np.inf, -np.inf], np.nan).fillna(0.0)


# =========================================================
# AI model wrapper
# =========================================================

class NILMAIExtension:
    def __init__(self, verbose=True):
        self.verbose = verbose
        print(f"[AI VERSION] {AI_VERSION}")

        self.state_model = joblib.load(STATE_MODEL_PATH)
        self.device_model = joblib.load(DEVICE_MODEL_PATH)
        self.state_info = load_json(STATE_FEATURE_INFO_PATH)
        self.device_info = load_json(DEVICE_FEATURE_INFO_PATH)

        self.state_labels = list(self.state_info.get("class_labels", list(getattr(self.state_model, "classes_", []))))
        self.device_labels = list(self.device_info.get("class_labels", list(getattr(self.device_model, "classes_", []))))
        self.state_feature_names = list(self.state_info.get("feature_names", []))
        self.device_feature_names = list(self.device_info.get("feature_names", []))
        self.window_size = int(self.state_info.get("window_size", WINDOW_SIZE_DEFAULT))

        self.block_buffer = deque(maxlen=self.window_size)
        self.state_history = deque(maxlen=STATE_SMOOTH_N)
        self.device_history = deque(maxlen=DEVICE_SMOOTH_N)
        self.last_result = None
        self.last_print_time = 0.0

        print("[AI INIT] state_model =", STATE_MODEL_PATH)
        print("[AI INIT] device_model =", DEVICE_MODEL_PATH)
        print("[AI INIT] state_classes =", self.state_labels)
        print("[AI INIT] device_classes =", self.device_labels)
        print("[AI INIT] state_feature_count =", len(self.state_feature_names))
        print("[AI INIT] device_feature_count =", len(self.device_feature_names))
        print("[AI INIT] window_size =", self.window_size)

    def reset(self):
        self.block_buffer.clear()
        self.state_history.clear()
        self.device_history.clear()

    def process_samples(self, ch0_block, ch1_block, fs):
        return self.process_block_features(compute_block_features(ch0_block, ch1_block, fs))

    def process_block_features(self, block_features):
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
                "block_features": dict(block_features),
            }
        return self._predict_current(block_features)

    def _predict_current(self, latest):
        X_state = make_window_features_from_blocks(self.block_buffer, self.state_feature_names)
        raw_state, state_conf, state_probs = predict_with_proba(self.state_model, X_state, self.state_labels)
        self.state_history.append(raw_state)
        smooth_state = majority_vote(list(self.state_history)) or raw_state
        state = self._apply_state_guard(raw_state, smooth_state, state_conf, state_probs, latest)

        device = None
        device_conf = 0.0
        device_probs = {}
        if state == "on":
            X_device = make_window_features_from_blocks(self.block_buffer, self.device_feature_names)
            raw_device, device_conf, device_probs = predict_with_proba(self.device_model, X_device, self.device_labels)
            # v21: use RF probability, but apply a physical plausibility guard.
            # The RF can call dryer low/mid/high as cooker; do not pass that stale/wrong
            # label into the tracker.
            device, device_conf = self._apply_device_guard(raw_device, device_conf, device_probs, latest)
        else:
            self.device_history.clear()

        result = {
            "ready": True,
            "version": AI_VERSION,
            "state": state,
            "raw_state": raw_state,
            "state_conf": float(state_conf),
            "state_probs": state_probs,
            "device": device,
            "device_conf": float(device_conf),
            "device_probs": device_probs,
            "Irms_adc": safe_float(latest.get("Irms_adc", 0.0)),
            "Pabs_mean_proxy": safe_float(latest.get("Pabs_mean_proxy", 0.0)),
            "H1_60_mag": safe_float(latest.get("H1_60_mag", 0.0)),
            "THD_i": safe_float(latest.get("THD_i", 0.0)),
            "fft_peak_freq": safe_float(latest.get("fft_peak_freq", 0.0)),
            "block_features": dict(latest),
        }
        self.last_result = result
        if self.verbose:
            self.print_result(result)
        return result

    def _apply_state_guard(self, raw_state, smooth_state, state_conf, state_probs, latest):
        # The state model is window-based and can lag after a device is turned off.
        # If the latest block is physically idle, do not let stale window prediction run the device model.
        if is_idle(latest):
            offp = safe_float(state_probs.get("plugged_off", 0.0))
            emptyp = safe_float(state_probs.get("empty", 0.0))
            return "plugged_off" if offp >= emptyp else "empty"
        p, i, h1 = triplet(latest).values()
        if p < 100.0 and i < 1.0 and h1 < 10.0:
            return "empty"
        onp = safe_float(state_probs.get("on", 0.0))
        # v26: do NOT convert rice-cooker plug/standby into ON.
        # Only let the device model see cooker when there is real running/ramp evidence.
        if is_cooker_plug_standby(latest, state_probs, raw_state):
            return "plugged_off"
        if is_cooker_running_signal(latest, state_probs, raw_state, None):
            return "on"
        # Legacy fallback for non-standby cooker-like ramp.
        if is_cooker_lock_seed(latest, None) and onp >= 0.50:
            return "on"
        if raw_state == "on" and state_conf < STATE_ON_MIN_CONF:
            offp = safe_float(state_probs.get("plugged_off", 0.0))
            emptyp = safe_float(state_probs.get("empty", 0.0))
            if max(offp, emptyp) > onp and not is_dryer_fast(latest):
                return "plugged_off" if offp >= emptyp else "empty"
        return smooth_state

    def _apply_device_guard(self, raw_device, conf, probs, latest):
        raw_device = normalize_device(raw_device)
        conf = safe_float(conf, 0.0)
        probs = probs or {}
        fan_p = safe_float(probs.get("fan", 0.0))
        cooker_p = safe_float(probs.get("cooker", 0.0))
        dryer_p = safe_float(probs.get("dryer", 0.0))
        charger_p = safe_float(probs.get("charger", 0.0))

        if is_idle(latest):
            return None, 0.0

        # Physical overrides first.
        # Cooker must be checked before fan, because the real cooker low region overlaps fan P/I/H1.
        cooker_ok = is_cooker_alive(latest, probs)
        if cooker_ok:
            return "cooker", max(conf if raw_device == "cooker" else cooker_p, cooker_p, 0.70 if is_cooker_low_profile(latest) else 0.65)

        # Dryer ramp/profile wins over weak cooker/fan RF labels. This prevents dryer-only
        # slow_low from becoming FAN_ON/COOKER_ON.
        if is_dryer_ramp_like(latest) or is_dryer_profile(latest):
            return "dryer", max(conf if raw_device == "dryer" else dryer_p, 0.82 if is_dryer_fast(latest) else 0.72)

        if is_fan_alive(latest):
            return "fan", max(conf if raw_device == "fan" else fan_p, 0.80)

        # Any cooker label outside the stricter physical cooker region is treated as unknown.
        if raw_device == "cooker":
            return "unknown_on", cooker_p

        if conf >= DEVICE_MIN_CONF:
            return raw_device, conf
        return "unknown_on", conf

    def print_result(self, result):
        now = time.time()
        if now - self.last_print_time < MIN_PRINT_INTERVAL_SEC:
            return
        self.last_print_time = now
        if not result.get("ready", False):
            print(f"[AI] {result.get('reason', 'not ready')}")
            return
        sp = format_prob_dict(result.get("state_probs", {}), topk=3)
        dp = format_prob_dict(result.get("device_probs", {}), topk=4)
        state = result["state"]
        if state == "on":
            print(
                f"[AI] STATE={state} raw={result['raw_state']} sconf={result['state_conf']:.2f} | "
                f"DEVICE={result['device']} dconf={result['device_conf']:.2f} | "
                f"I={result['Irms_adc']:.2f}, Pabs={result['Pabs_mean_proxy']:.1f}, "
                f"H1={result['H1_60_mag']:.1f}, THD={result['THD_i']:.3f} | "
                f"state_probs[{sp}] | device_probs[{dp}]"
            )
        else:
            print(
                f"[AI] STATE={state} raw={result['raw_state']} sconf={result['state_conf']:.2f} | "
                f"DEVICE=None | I={result['Irms_adc']:.2f}, Pabs={result['Pabs_mean_proxy']:.1f}, "
                f"H1={result['H1_60_mag']:.1f}, THD={result['THD_i']:.3f} | state_probs[{sp}]"
            )

    def predict_device_from_feature_dict(self, feature_dict):
        X = make_window_features_from_blocks([feature_dict] * self.window_size, self.device_feature_names)
        return predict_with_proba(self.device_model, X, self.device_labels)


# =========================================================
# Public helper API
# =========================================================

_global_ai = None


def init_ai(verbose=True):
    global _global_ai
    _global_ai = NILMAIExtension(verbose=verbose)
    return _global_ai


def process_samples(ch0_block, ch1_block, fs):
    global _global_ai
    if _global_ai is None:
        _global_ai = NILMAIExtension(verbose=True)
    return _global_ai.process_samples(ch0_block, ch1_block, fs)


def process_block_features(block_features):
    global _global_ai
    if _global_ai is None:
        _global_ai = NILMAIExtension(verbose=True)
    return _global_ai.process_block_features(block_features)


# =========================================================
# Dashboard/main adapter
# =========================================================

try:
    from dsp_engine import DSPEngine
    from dashboard_ui import DashboardUI
except Exception as e:
    DSPEngine = None
    DashboardUI = None
    _ADAPTER_IMPORT_ERROR = e
else:
    _ADAPTER_IMPORT_ERROR = None


class DeltaMultiDeviceTracker:
    def __init__(self, ai_extension, verbose=True):
        self.ai = ai_extension
        self.verbose = verbose
        self.history = deque(maxlen=DELTA_HISTORY_N)
        self.active = []
        self.off_events = deque(maxlen=MAX_SLOTS)
        self.retained_off_slots = {}
        self.device_slot_memory = {}
        self.cooldown = 0
        self.latest_features = None
        self.latest_ai = None
        self.idle_hits = 0
        self.fast_dryer_hits = 0
        self.abs_sync_hits = {}
        self.dryer_baseline = None
        self.fan_missing_hits = 0
        self.post_dryer_off_left = 0
        self.cooker_lock_left = 0
        self.cooker_low_hits = 0
        self.cooker_standby_hits = 0
        self.cooker_with_dryer_hits = 0
        self.cooker_heat_hold_left = 0
        self.cooker_low_after_heat_hits = 0

    def update(self, ai_result):
        if not ai_result or not ai_result.get("ready", False):
            return self._output(ai_result)

        latest = ai_result.get("block_features") or {
            "Pabs_mean_proxy": ai_result.get("Pabs_mean_proxy", 0.0),
            "Irms_adc": ai_result.get("Irms_adc", 0.0),
            "H1_60_mag": ai_result.get("H1_60_mag", 0.0),
            "THD_i": ai_result.get("THD_i", 0.0),
        }
        self.latest_features = dict(latest)
        self.latest_ai = ai_result
        self.history.append(dict(latest))

        if self._is_cooker_plug_standby_result(ai_result, latest):
            self._handle_cooker_plug_standby(latest)
        self._refresh_cooker_lock(latest, ai_result.get("device_probs", {}) or {})

        self._age_items()
        self._tick_off_events()
        self._update_dryer_baseline()
        self._sync_absolute(ai_result, latest)
        self._drop_false_cooker_if_needed(latest)
        self._recover_fan_after_dryer_off(ai_result, latest)
        self._check_fan_missing_over_dryer(latest)
        self._clear_idle_if_needed(latest)
        self._update_cooker_off_state(ai_result, latest)

        event = None
        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            event = self._detect_event()
            if event:
                if event["type"] == "on":
                    self._handle_on(event, ai_result, latest)
                else:
                    self._handle_off(event, ai_result, latest)
                self.cooldown = EVENT_COOLDOWN_BLOCKS

        return self._output(ai_result, event)

    def _age_items(self):
        for item in self.active:
            item["age"] = int(item.get("age", 0)) + 1

    def _cooker_lock_active(self):
        return self.cooker_lock_left > 0 or self._active_device("cooker")

    def _is_cooker_plug_standby_result(self, ai_result, latest):
        state_probs = ai_result.get("state_probs", {}) or {}
        raw_state = ai_result.get("raw_state", ai_result.get("state", ""))
        return is_cooker_plug_standby(latest, state_probs, raw_state)

    def _is_cooker_running_result(self, ai_result, latest):
        state_probs = ai_result.get("state_probs", {}) or {}
        raw_state = ai_result.get("raw_state", ai_result.get("state", ""))
        probs = ai_result.get("device_probs", {}) or {}
        return is_cooker_running_signal(latest, state_probs, raw_state, probs)

    def _handle_cooker_plug_standby(self, latest):
        # 2 consecutive standby-like blocks: show/keep COOKER_OFF, not COOKER_ON.
        self.cooker_standby_hits += 1
        self.cooker_low_hits = 0
        if self.cooker_standby_hits < COOKER_STANDBY_HITS_REQUIRED:
            return

        if self._active_device("cooker"):
            # If cooker was ON and settles back to plug/standby for several blocks,
            # treat it as cooker OFF rather than keeping ON forever.
            if self.cooker_standby_hits >= COOKER_OFF_HITS_TO_REMOVE_ACTIVE:
                self._remove_device("cooker", conf=0.80, source="cooker_plug_standby")
            return

        # Remember socket/device as OFF. This gives UI: COOKER_OFF.
        dev = "cooker"
        if dev in self.device_slot_memory and self._slot_available(self.device_slot_memory[dev], dev):
            slot = int(self.device_slot_memory[dev])
        else:
            slot = self._slot_for_device(dev)
        already = self.retained_off_slots.get(slot, {}).get("device") == dev
        self.retained_off_slots[slot] = {"device": dev, "conf": 0.80, "source": "cooker_plug_standby"}
        self.device_slot_memory[dev] = slot
        self._remove_off_event(dev)
        if self.verbose and not already:
            print(f"[DELTA PLUG] COOKER retained as OFF slot={slot + 1} source=cooker_plug_standby")

    def _refresh_cooker_lock(self, latest, probs):
        # v26: cooker plug/standby must not seed COOKER_ON lock.
        ai = self.latest_ai or {}
        if self._is_cooker_plug_standby_result(ai, latest):
            if not self._active_device("cooker"):
                self.cooker_lock_left = 0
            return

        # Confirm cooker running seed with 2 hits to avoid one-block noise. Once active,
        # cooker lock is refreshed continuously until idle.
        if self._is_cooker_running_result(ai, latest):
            self.cooker_standby_hits = 0
            self.cooker_low_hits += 1
        elif is_idle(latest):
            self.cooker_low_hits = 0
            self.cooker_standby_hits = 0
        else:
            self.cooker_low_hits = max(0, self.cooker_low_hits - 1)
            self.cooker_standby_hits = max(0, self.cooker_standby_hits - 1)

        if self._active_device("cooker") or self.cooker_low_hits >= COOKER_LOW_CONFIRM_HITS_REQUIRED:
            self.cooker_lock_left = COOKER_LOCK_BLOCKS
        elif self.cooker_lock_left > 0:
            if is_idle(latest):
                self.cooker_lock_left = max(0, self.cooker_lock_left - 8)
            else:
                self.cooker_lock_left -= 1

    def _is_cooker_high_activity(self, latest):
        t = abs_triplet(latest)
        return (
            t["Pabs_mean_proxy"] >= COOKER_HIGH_ACTIVITY_PABS_MIN or
            t["Irms_adc"] >= COOKER_HIGH_ACTIVITY_IRMS_MIN or
            t["H1_60_mag"] >= COOKER_HIGH_ACTIVITY_H1_MIN
        )

    def _is_cooker_low_after_on(self, latest):
        t = abs_triplet(latest)
        return (
            COOKER_LOW_PABS_MIN <= t["Pabs_mean_proxy"] <= COOKER_LOW_AFTER_ON_PABS_MAX and
            COOKER_LOW_IRMS_MIN <= t["Irms_adc"] <= COOKER_LOW_AFTER_ON_IRMS_MAX and
            COOKER_LOW_H1_MIN <= t["H1_60_mag"] <= COOKER_LOW_AFTER_ON_H1_MAX
        )

    def _update_cooker_off_state(self, ai_result, latest):
        """v29: turn COOKER_ON back into COOKER_OFF after long low/standby period.

        Rice cooker cycles: a short low period after a heater pulse is normal,
        so we keep COOKER_ON while cooker_heat_hold_left remains.  If no high
        activity appears for many blocks and the measured load is back to the
        low cooker/standby range, we remove only cooker and retain the slot as
        COOKER_OFF.
        """
        if not self._active_device("cooker"):
            self.cooker_heat_hold_left = 0
            self.cooker_low_after_heat_hits = 0
            return
        if self._active_device("dryer"):
            # Dryer is being tracked separately; do not use the summed signal to
            # decide cooker OFF.
            self.cooker_heat_hold_left = max(self.cooker_heat_hold_left, 4)
            self.cooker_low_after_heat_hits = 0
            return
        if is_idle(latest):
            self._remove_device("cooker", conf=0.90, source="cooker_idle_off")
            self.cooker_heat_hold_left = 0
            self.cooker_low_after_heat_hits = 0
            return
        if self._is_cooker_high_activity(latest):
            self.cooker_heat_hold_left = COOKER_HEAT_HOLD_BLOCKS
            self.cooker_low_after_heat_hits = 0
            return
        if self.cooker_heat_hold_left > 0:
            self.cooker_heat_hold_left -= 1
            self.cooker_low_after_heat_hits = 0
            return
        if self._is_cooker_low_after_on(latest):
            self.cooker_low_after_heat_hits += 1
        else:
            self.cooker_low_after_heat_hits = max(0, self.cooker_low_after_heat_hits - 1)
        if self.cooker_low_after_heat_hits >= COOKER_LOW_OFF_HITS_REQUIRED:
            self._remove_device("cooker", conf=0.85, source="cooker_low_settled_off")
            self.cooker_lock_left = 0
            self.cooker_low_hits = 0
            self.cooker_standby_hits = max(self.cooker_standby_hits, COOKER_STANDBY_HITS_REQUIRED)
            self.cooker_low_after_heat_hits = 0

    def _detect_event(self):
        if len(self.history) < DELTA_OLD_N + DELTA_NEW_N:
            return None
        rows = list(self.history)
        old = self._mean(rows[-(DELTA_OLD_N + DELTA_NEW_N):-DELTA_NEW_N])
        new = self._mean(rows[-DELTA_NEW_N:])
        delta = sub_triplet(new, old)
        axes_pos = int(delta["Pabs_mean_proxy"] >= ON_DELTA_PABS_MIN) + int(delta["Irms_adc"] >= ON_DELTA_IRMS_MIN) + int(delta["H1_60_mag"] >= ON_DELTA_H1_MIN)
        axes_neg = int(delta["Pabs_mean_proxy"] <= -ON_DELTA_PABS_MIN) + int(delta["Irms_adc"] <= -ON_DELTA_IRMS_MIN) + int(delta["H1_60_mag"] <= -ON_DELTA_H1_MIN)
        if axes_pos >= EVENT_SCORE_MIN:
            return {"type": "on", "old_mean": old, "new_mean": new, "delta": delta}
        if axes_neg >= EVENT_SCORE_MIN:
            return {"type": "off", "old_mean": old, "new_mean": new, "delta": delta}
        return None

    def _mean(self, rows):
        if not rows:
            return {}
        out = {}
        for col in BASE_FEATURE_COLS:
            vals = [safe_float(r.get(col, 0.0)) for r in rows]
            out[col] = float(np.mean(vals)) if vals else 0.0
        return out

    def _active_device(self, device):
        device = normalize_device(device)
        return any(x.get("device") == device for x in self.active)

    def _get_active(self, device):
        device = normalize_device(device)
        for item in self.active:
            if item.get("device") == device:
                return item
        return None

    def _retained_off_device(self, device):
        device = normalize_device(device)
        return any(info.get("device") == device for info in self.retained_off_slots.values())

    def _cooker_off_start_candidate(self, latest, probs=None):
        # Single authority for COOKER_OFF -> COOKER_ON ownership.
        return self._retained_off_device("cooker") and (not self._active_device("dryer")) and is_cooker_start_from_off(latest, probs or {})

    def _promote_cooker_from_off(self, latest, probs=None, event=None, source="cooker_off_start"):
        probs = probs or {}
        self._add_or_update("cooker", max(safe_float(probs.get("cooker", 0.0)), COOKER_LOCK_CONF), probs, latest, event, source=source)
        self.cooker_lock_left = COOKER_LOCK_BLOCKS
        self.cooker_heat_hold_left = COOKER_HEAT_HOLD_BLOCKS
        self.cooker_low_after_heat_hits = 0
        self.cooker_with_dryer_hits = 0
        self.fast_dryer_hits = 0
        self.post_dryer_off_left = 0
        self.dryer_baseline = None
        # The first cooker heater pulse must not leave stale dryer/fan/off residues.
        self._drop_false_active("dryer", reason="cooker_off_start")
        self._drop_false_active("fan", reason="cooker_off_start")
        self.off_events = deque([x for x in self.off_events if x.get("device") not in {"dryer", "fan"}], maxlen=MAX_SLOTS)
        for s, info in list(self.retained_off_slots.items()):
            if info.get("device") in {"dryer", "fan"}:
                self.retained_off_slots.pop(s, None)
        return True

    def _sync_absolute(self, ai_result, latest):
        state = str(ai_result.get("state", "empty")).lower()
        probs_state = ai_result.get("state_probs", {}) or {}
        on_prob = safe_float(probs_state.get("on", 0.0))
        device = normalize_device(ai_result.get("device"))
        conf = safe_float(ai_result.get("device_conf", 0.0))
        probs = ai_result.get("device_probs", {}) or {}

        # v26: if latest is only cooker plug/standby, do not refresh COOKER_ON.
        if self._is_cooker_plug_standby_result(ai_result, latest) and not self._active_device("dryer"):
            return

        # v25: cooker lock protects cooker, but must allow a real dryer to be
        # added later.  If dryer evidence is persistent, keep COOKER_ON and add
        # DRYER_ON instead of swallowing the dryer as cooker ramp.
        if self._cooker_lock_active() and is_cooker_ramp_under_lock(latest):
            dryer_candidate_now = is_separate_dryer_candidate_under_cooker(latest, probs, device, conf)
            if dryer_candidate_now:
                self.cooker_with_dryer_hits = min(20, self.cooker_with_dryer_hits + 1)
            else:
                # v28: reset hard.  Otherwise old dryer hits keep re-adding DRYER_ON
                # during cooker-only low blocks after the heater cycles down.
                self.cooker_with_dryer_hits = 0

            self._add_or_update("cooker", max(safe_float(probs.get("cooker", 0.0)), COOKER_LOCK_CONF), probs, latest, source="cooker_lock")

            if dryer_candidate_now and self.cooker_with_dryer_hits >= COOKER_WITH_DRYER_HITS_REQUIRED:
                self._add_or_update("dryer", max(conf, safe_float(probs.get("dryer", 0.0)), 0.82), probs, latest, source="cooker_plus_dryer_sync")
                self._drop_false_active("fan", reason="cooker_plus_dryer")
            else:
                # Before separate dryer is confirmed, suppress only false fan.
                self._drop_false_active("fan", reason="cooker_lock")
                if self._active_device("dryer") and not is_dryer_alive(latest):
                    self._drop_false_active("dryer", reason="cooker_lock_no_dryer_signal")
            return

        if state != "on" and on_prob < 0.45:
            self.abs_sync_hits.clear()
            return

        # v30: if the cooker was retained as OFF, the first heater pulse belongs
        # to that cooker unless dryer is clearly RF-dominant.  This prevents
        # COOKER_OFF -> DRYER_ON during cooker-only tests.
        if self._cooker_off_start_candidate(latest, probs):
            self._promote_cooker_from_off(latest, probs, source="cooker_off_start_abs")
            return

        # Fast dryer sync even when state/model confidence lags.
        # v23: do not fast-sync dryer when the same absolute block is cooker-like.
        dryer_prob = safe_float(probs.get("dryer", 0.0))
        if (is_dryer_ramp_like(latest) or is_dryer_profile(latest)) and not is_cooker_alive(latest, probs):
            self.fast_dryer_hits += 1
            if self.fast_dryer_hits >= DRYER_FAST_HITS_REQUIRED:
                self._add_or_update("dryer", max(conf, 0.80, dryer_prob), probs, latest, source="fast_absolute_sync")
                self._drop_false_active("cooker", reason="dryer_profile")
                return
        else:
            self.fast_dryer_hits = max(0, self.fast_dryer_hits - 1)

        if device not in {"fan", "charger", "cooker"}:
            return

        if device == "fan":
            ok = (
                on_prob >= FAN_ABS_ON_PROB_MIN and
                conf >= FAN_ABS_CONF_MIN and
                is_fan_alive(latest) and
                not is_cooker_alive(latest, probs)
            )
        elif device == "charger":
            ok = (
                on_prob >= CHARGER_ABS_ON_PROB_MIN and
                conf >= CHARGER_ABS_CONF_MIN and
                not is_fan_alive(latest) and
                not is_cooker_alive(latest, probs) and
                not is_dryer_alive(latest)
            )
        else:  # cooker
            cooker_prob = safe_float(probs.get("cooker", 0.0))
            ok = (
                max(conf, cooker_prob) >= COOKER_ABS_CONF_MIN and
                self._is_cooker_running_result(ai_result, latest)
            )
            conf = max(conf, cooker_prob)

        key = f"abs_{device}"
        if ok:
            self.abs_sync_hits[key] = self.abs_sync_hits.get(key, 0) + 1
        else:
            self.abs_sync_hits[key] = max(0, self.abs_sync_hits.get(key, 0) - 1)

        if self.abs_sync_hits.get(key, 0) >= ABS_SYNC_HITS_REQUIRED:
            self._add_or_update(device, conf, probs, latest, source="absolute_sync")

    def _drop_false_cooker_if_needed(self, latest):
        # If cooker is active but the measured signal is clearly fan or dryer and not
        # cooker-prototype-like, it is a false stack entry from model ambiguity.
        if not self._active_device("cooker"):
            return
        if self._cooker_lock_active():
            return
        probs = (self.latest_ai or {}).get("device_probs", {}) or {}
        if is_cooker_alive(latest, probs):
            return
        if is_dryer_profile(latest) or is_fan_alive(latest):
            self._drop_false_active("cooker", reason="measured_not_cooker")

    def _handle_on(self, event, ai_result, latest):
        delta = dict(event["delta"])
        device, conf, probs = self.ai.predict_device_from_feature_dict({
            **{c: 0.0 for c in BASE_FEATURE_COLS},
            "Pabs_mean_proxy": max(0.0, delta["Pabs_mean_proxy"]),
            "Irms_adc": max(0.0, delta["Irms_adc"]),
            "H1_60_mag": max(0.0, delta["H1_60_mag"]),
            "THD_i": safe_float(latest.get("THD_i", 0.0)),
        })
        device = normalize_device(device)
        dryer_active = self._active_device("dryer") or is_dryer_alive(event.get("old_mean", {}))

        new_mean = event.get("new_mean", {}) or {}
        cooker_prob = safe_float(probs.get("cooker", 0.0))
        dryer_prob = safe_float(probs.get("dryer", 0.0))

        # v31: COOKER_OFF -> first large heater pulse has priority over every other ON path.
        latest_probs_for_start = ai_result.get("device_probs", {}) or probs or {}
        if self._cooker_off_start_candidate(latest, latest_probs_for_start):
            self._promote_cooker_from_off(latest, latest_probs_for_start, event=event, source="cooker_off_start_delta")
            return

        # v26: plug/standby pulses are not cooker ON.
        if self._is_cooker_plug_standby_result(ai_result, latest) and not self._active_device("cooker"):
            self._handle_cooker_plug_standby(latest)
            return

        # v25: under cooker lock, a positive delta can be either cooker heating
        # ramp or a newly switched-on dryer. Require persistent dryer evidence
        # before adding DRYER_ON; otherwise keep the signal as COOKER_ON.
        if self._cooker_lock_active() and is_cooker_ramp_under_lock(latest):
            latest_probs = ai_result.get("device_probs", {}) or {}
            abs_device = normalize_device(ai_result.get("device"))
            abs_conf = safe_float(ai_result.get("device_conf", 0.0))
            dryer_candidate_now = is_separate_dryer_candidate_under_cooker(latest, latest_probs, abs_device, abs_conf)
            if dryer_candidate_now:
                self.cooker_with_dryer_hits = min(20, self.cooker_with_dryer_hits + 1)
            else:
                self.cooker_with_dryer_hits = 0

            self._add_or_update("cooker", max(cooker_prob, safe_float(latest_probs.get("cooker", 0.0)), COOKER_LOCK_CONF), latest_probs or probs, latest, event, source="cooker_lock_delta")

            if dryer_candidate_now and self.cooker_with_dryer_hits >= COOKER_WITH_DRYER_HITS_REQUIRED:
                self._add_or_update("dryer", max(abs_conf, safe_float(latest_probs.get("dryer", 0.0)), 0.82), latest_probs, latest, event, source="cooker_plus_dryer_delta")
                self._drop_false_active("fan", reason="cooker_plus_dryer")
            else:
                self._drop_false_active("fan", reason="cooker_lock_delta")
                if self._active_device("dryer") and not is_dryer_alive(latest):
                    self._drop_false_active("dryer", reason="cooker_lock_delta_no_dryer_signal")
            return

        # Cooker first, but only when it is running/heating. Low plug/standby stays COOKER_OFF.
        latest_cooker_ok = self._is_cooker_running_result(ai_result, latest)
        new_cooker_ok = is_cooker_mid_profile(new_mean, probs) or (is_cooker_low_profile(new_mean) and safe_float((ai_result.get("state_probs", {}) or {}).get("on", 0.0)) >= COOKER_RUN_ON_PROB_MIN)
        if (latest_cooker_ok or new_cooker_ok) and not is_strong_dryer(latest):
            device = "cooker"
            conf = max(conf, cooker_prob, 0.70 if is_cooker_low_profile(latest) or is_cooker_low_profile(new_mean) else 0.62)

        # Dryer physical profile must win over weak model ambiguity. Use latest as well as
        # new_mean so the very first dryer slow_low step is not accepted as FAN_ON.
        elif (is_dryer_ramp_like(latest) or is_dryer_profile(new_mean) or is_dryer_ramp_like(new_mean)):
            device = "dryer"
            conf = max(conf, dryer_prob, 0.88 if is_strong_dryer(latest) or is_strong_dryer(new_mean) else 0.80)

        # Fan over dryer: keep it alive even if RF delta is uncertain.
        elif dryer_active and is_fan_like_delta(delta, dryer_active=True) and not is_cooker_alive(new_mean, probs):
            device = "fan"
            conf = max(conf, 0.84)

        # Standalone fan requires the resulting load itself to be fan-like.
        elif device == "fan":
            if (not is_fan_like_delta(delta, dryer_active=False)) or (not is_fan_alive(new_mean)) or is_cooker_alive(new_mean, probs) or is_dryer_profile(new_mean):
                if self.verbose:
                    print(
                        "[DELTA EVENT] FAN ON ignored: not standalone fan-sized | "
                        f"dPabs={delta['Pabs_mean_proxy']:.1f}, dI={delta['Irms_adc']:.2f}, dH1={delta['H1_60_mag']:.1f}"
                    )
                return

        # Charger/cooker sanity checks.
        if device == "charger" and (conf < CHARGER_DELTA_CONF_MIN or is_fan_alive(event.get("new_mean", {})) or is_cooker_alive(event.get("new_mean", {}), probs) or is_dryer_alive(event.get("new_mean", {}))):
            if self.verbose:
                print(f"[DELTA EVENT] ON CHARGER ignored: weak/implausible conf={conf:.2f}")
            return
        if device == "cooker":
            cooker_ok_for_delta = self._is_cooker_running_result(ai_result, latest) or is_cooker_mid_profile(event.get("new_mean", {}), probs)
            if conf < COOKER_DELTA_CONF_MIN or not cooker_ok_for_delta:
                if self._is_cooker_plug_standby_result(ai_result, latest):
                    self._handle_cooker_plug_standby(latest)
                    if self.verbose:
                        print(f"[DELTA EVENT] ON COOKER held as OFF: plug/standby conf={conf:.2f}")
                elif self.verbose:
                    print(f"[DELTA EVENT] ON COOKER ignored: weak/implausible conf={conf:.2f}")
                return
        if conf < DELTA_DEVICE_MIN_CONF:
            if self.verbose:
                print(
                    "[DELTA EVENT] ON detected but device unknown | "
                    f"dPabs={delta['Pabs_mean_proxy']:.1f}, dI={delta['Irms_adc']:.2f}, dH1={delta['H1_60_mag']:.1f}"
                )
            return

        self._add_or_update(device, conf, probs, latest, event, source="delta")

    def _handle_off(self, event, ai_result, latest):
        if not self.active:
            return
        # v25: during cooker lock, negative deltas are usually cooker heating duty
        # changes. But if DRYER_ON was separately confirmed and the latest block
        # has fallen back to cooker-like/non-dryer levels, remove only dryer.
        if self._active_device("cooker") and self._cooker_lock_active() and not is_idle(latest):
            latest_probs = ai_result.get("device_probs", {}) or {}
            if self._active_device("dryer") and (not is_dryer_alive(latest)) and is_cooker_alive(latest, latest_probs):
                self._remove_device("dryer", conf=0.90, source="cooker_plus_dryer_off")
                self.cooker_with_dryer_hits = 0
                return
            if self._active_device("dryer") and is_dryer_alive(latest):
                # keep both cooker and dryer through dryer mode changes
                self._add_or_update("cooker", COOKER_LOCK_CONF, latest_probs, latest, source="cooker_lock_hold")
                return
            self._add_or_update("cooker", COOKER_LOCK_CONF, latest_probs, latest, source="cooker_lock_hold")
            return
        delta_abs = abs_triplet(event["delta"])

        # If dryer drops and fan-like feature remains, dryer went OFF and fan survived.
        if self._active_device("dryer") and is_fan_alive(latest) and not is_dryer_alive(latest):
            self._remove_device("dryer", conf=0.90, source="delta_off")
            self.post_dryer_off_left = 25
            if not self._active_device("fan"):
                self._add_or_update("fan", 0.80, ai_result.get("device_probs", {}) or {}, latest, source="post_dryer_off_absolute")
            return

        # If fan remains alive, do not remove fan by a negative delta caused by dryer mode changes.
        if self._active_device("fan") and is_fan_alive(latest):
            # Still allow dryer OFF if dryer is no longer alive.
            if self._active_device("dryer") and not is_dryer_alive(latest):
                self._remove_device("dryer", conf=0.90, source="delta_off")
            else:
                if self.verbose:
                    print(
                        "[DELTA EVENT] OFF canceled: fan still alive / dryer mode change | "
                        f"dPabs={event['delta']['Pabs_mean_proxy']:.1f}, dI={event['delta']['Irms_adc']:.2f}, dH1={event['delta']['H1_60_mag']:.1f}"
                    )
            return

        # Choose active item whose signature is closest to the removed magnitude.
        best = None
        best_dist = float("inf")
        for item in self.active:
            sig = item.get("signature", {}) or {}
            st = triplet(sig)
            dist = abs(delta_abs["Pabs_mean_proxy"] - st["Pabs_mean_proxy"]) / max(st["Pabs_mean_proxy"], 1.0)
            dist += abs(delta_abs["Irms_adc"] - st["Irms_adc"]) / max(st["Irms_adc"], 1.0)
            dist += abs(delta_abs["H1_60_mag"] - st["H1_60_mag"]) / max(st["H1_60_mag"], 1.0)
            if dist < best_dist:
                best_dist = dist
                best = item

        if best:
            # Dryer mode-down is not dryer OFF if dryer-sized signal remains.
            if best["device"] == "dryer" and is_dryer_alive(latest):
                best["signature"] = triplet(latest)
                if self.verbose:
                    print("[DELTA EVENT] OFF DRYER canceled: dryer mode change/still alive")
                return
            self._remove_device(best["device"], conf=0.80, source="delta_off")

    def _add_or_update(self, device, conf, probs, latest, event=None, source="delta"):
        device = normalize_device(device)
        if device is None:
            return False
        if device == "cooker":
            self.cooker_lock_left = COOKER_LOCK_BLOCKS
            self.cooker_low_hits = max(self.cooker_low_hits, COOKER_LOW_CONFIRM_HITS_REQUIRED)
            if self._is_cooker_high_activity(latest):
                self.cooker_heat_hold_left = COOKER_HEAT_HOLD_BLOCKS
                self.cooker_low_after_heat_hits = 0

        existing = self._get_active(device)
        if existing:
            existing["conf"] = max(safe_float(existing.get("conf", 0.0)), safe_float(conf, 0.0))
            existing["signature"] = triplet(latest)
            existing["source"] = source if existing.get("source") != "absolute_sync" else existing.get("source")
            existing["age"] = 0
            self._clear_retained_off(device=device, slot=existing["slot"])
            if device == "cooker":
                self._drop_false_active("fan", reason="cooker_update")
                # Do not erase a separately confirmed dryer just because cooker is
                # being refreshed during COOKER_ON + DRYER_ON.
                if self._active_device("dryer") and not is_dryer_alive(latest):
                    self._drop_false_active("dryer", reason="cooker_update_no_dryer_signal")
            if self.verbose and event is not None:
                print(f"[DELTA EVENT] ON update {device.upper()} conf={conf:.2f} source={source}")
            return True

        # v23: before assigning a slot for a real cooker, clear false dryer/fan
        # residues so cooker can reuse the first slot instead of being pushed to slot 2/3.
        if device == "cooker" and is_cooker_alive(latest, probs) and not is_strong_dryer(latest):
            if self._active_device("dryer") and not is_dryer_alive(latest):
                self._drop_false_active("dryer", reason="cooker_profile_no_dryer_signal")
            if self._active_device("fan"):
                self._drop_false_active("fan", reason="cooker_profile")

        slot = self._slot_for_device(device)
        item = {
            "device": device,
            "slot": slot,
            "conf": safe_float(conf, 0.0),
            "signature": triplet(latest),
            "probs": probs or {},
            "source": source,
            "age": 0,
        }
        self.active.append(item)
        self.device_slot_memory[device] = slot
        self._clear_retained_off(device=device, slot=slot)
        self._remove_off_event(device)

        # If dryer is added while fan is already active, estimate dryer-only baseline.
        if device == "dryer" and self._active_device("fan"):
            fan_item = self._get_active("fan")
            fsig = fan_item.get("signature", {}) if fan_item else {}
            self.dryer_baseline = {
                "Pabs_mean_proxy": max(0.0, safe_float(latest.get("Pabs_mean_proxy", 0.0)) - safe_float(fsig.get("Pabs_mean_proxy", 0.0))),
                "Irms_adc": max(0.0, safe_float(latest.get("Irms_adc", 0.0)) - safe_float(fsig.get("Irms_adc", 0.0))),
                "H1_60_mag": max(0.0, safe_float(latest.get("H1_60_mag", 0.0)) - safe_float(fsig.get("H1_60_mag", 0.0))),
            }

        # v23: if cooker is accepted, clear false dryer/fan residues from earlier
        # cooker ramp misclassification. This prevents COOKER_ON from becoming
        # DRYER_ON + FAN_ON + COOKER_ON during cooker-only tests.
        if device == "cooker":
            if self._active_device("dryer") and is_cooker_alive(latest, probs) and not is_dryer_alive(latest):
                self._drop_false_active("dryer", reason="cooker_profile_no_dryer_signal")
            if self._active_device("fan") and is_cooker_alive(latest, probs):
                self._drop_false_active("fan", reason="cooker_profile")

        if self.verbose:
            msg = f"[DELTA EVENT] ON {device.upper()} slot={slot + 1} conf={conf:.2f} source={source}"
            if event is not None:
                d = event["delta"]
                msg += f" | dPabs={d['Pabs_mean_proxy']:.1f}, dI={d['Irms_adc']:.2f}, dH1={d['H1_60_mag']:.1f}"
            print(msg)
        return True

    def _drop_false_active(self, device, reason="implausible"):
        """Silently remove an active false positive without leaving OFF memory.

        This is intentionally used only for cooker false positives caused by RF/model
        ambiguity during dryer-only tests. Real user OFF events still go through
        _remove_device and keep persistent OFF state.
        """
        device = normalize_device(device)
        before = len(self.active)
        self.active = [x for x in self.active if x.get("device") != device]
        removed_active = len(self.active) != before
        if removed_active and self.verbose:
            print(f"[DELTA STACK] dropped false {device.upper()} active | reason={reason}")
        self.off_events = deque([x for x in self.off_events if x.get("device") != device], maxlen=MAX_SLOTS)
        # v30: do not erase persistent COOKER_OFF memory when there was no active
        # cooker to drop.  v29 cleared retained_off_slots during dryer false-positive
        # cleanup, which caused COOKER_OFF -> EMPTY/DRYER_ON.
        if removed_active:
            remove_slots = [s for s, info in self.retained_off_slots.items() if info.get("device") == device]
            for s in remove_slots:
                self.retained_off_slots.pop(s, None)
        return removed_active

    def _remove_device(self, device, conf=0.80, source="off"):
        device = normalize_device(device)
        removed = None
        remain = []
        for item in self.active:
            if removed is None and item.get("device") == device:
                removed = item
            else:
                remain.append(item)
        self.active = remain
        if removed is None:
            return False
        self.device_slot_memory[device] = removed["slot"]
        self.off_events.append({"device": device, "slot": removed["slot"], "hold": OFF_HOLD_BLOCKS, "conf": conf, "source": source})
        if device == "dryer":
            self.post_dryer_off_left = 25
            self.dryer_baseline = None
        if device == "cooker":
            self.cooker_lock_left = 0
            self.cooker_low_hits = 0
            self.cooker_standby_hits = 0
            self.cooker_with_dryer_hits = 0
        if self.verbose:
            print(f"[DELTA EVENT] OFF {device.upper()} slot={removed['slot'] + 1} conf={conf:.2f} source={source}")
        return True

    def _clear_idle_if_needed(self, latest):
        if is_idle(latest):
            self.idle_hits += 1
        else:
            self.idle_hits = 0
        if self.idle_hits < IDLE_CLEAR_HITS_REQUIRED:
            return
        # Move all active devices to persistent OFF, not EMPTY.
        while self.active:
            dev = self.active[0]["device"]
            self._remove_device(dev, conf=0.80, source="stale_idle_clear")

    def _update_dryer_baseline(self):
        latest = self.latest_features or {}
        if not self._active_device("dryer"):
            self.dryer_baseline = None
            self.fan_missing_hits = 0
            return
        if self._active_device("fan"):
            return
        if is_dryer_alive(latest):
            if self.dryer_baseline is None:
                self.dryer_baseline = triplet(latest)
            else:
                old = self.dryer_baseline
                self.dryer_baseline = {
                    "Pabs_mean_proxy": 0.85 * safe_float(old.get("Pabs_mean_proxy")) + 0.15 * safe_float(latest.get("Pabs_mean_proxy")),
                    "Irms_adc": 0.85 * safe_float(old.get("Irms_adc")) + 0.15 * safe_float(latest.get("Irms_adc")),
                    "H1_60_mag": 0.85 * safe_float(old.get("H1_60_mag")) + 0.15 * safe_float(latest.get("H1_60_mag")),
                }

    def _check_fan_missing_over_dryer(self, latest):
        if not (self._active_device("dryer") and self._active_device("fan") and self.dryer_baseline is not None):
            self.fan_missing_hits = 0
            return
        res = sub_triplet(latest, self.dryer_baseline)
        if is_mode_transition_residual(res):
            self.fan_missing_hits = 0
            if self.verbose:
                print(
                    "[DELTA RESIDUAL] FAN_OFF held: dryer mode transition/baseline mismatch | "
                    f"rPabs={res['Pabs_mean_proxy']:.1f}, rI={res['Irms_adc']:.2f}, rH1={res['H1_60_mag']:.1f}"
                )
            return
        if is_fan_residual(res):
            self.fan_missing_hits = 0
            return
        if is_fan_missing_residual(res):
            self.fan_missing_hits += 1
        else:
            self.fan_missing_hits = max(0, self.fan_missing_hits - 1)
        if self.fan_missing_hits >= FAN_MISSING_HITS_REQUIRED:
            self._remove_device("fan", conf=0.80, source="dryer_residual_missing")
            self.fan_missing_hits = 0

    def _recover_fan_after_dryer_off(self, ai_result, latest):
        if self.post_dryer_off_left <= 0:
            return
        if self._cooker_lock_active():
            self.post_dryer_off_left = 0
            return
        self.post_dryer_off_left -= 1
        probs = ai_result.get("device_probs", {}) or {}
        # v23: cooker low overlaps fan. After a false dryer OFF, do not recover FAN
        # if the remaining signal is cooker-like.
        if is_cooker_alive(latest, probs):
            return
        if is_fan_alive(latest) and not self._active_device("fan"):
            self._add_or_update("fan", 0.80, probs, latest, source="post_dryer_off_absolute")
            if self.verbose:
                print("[DELTA RECOVERY] FAN restored after DRYER_OFF by absolute feature")

    def _tick_off_events(self):
        kept = []
        for item in self.off_events:
            item["hold"] = int(item.get("hold", 0)) - 1
            if item["hold"] > 0:
                kept.append(item)
            else:
                self._remember_retained_off(item)
        self.off_events = deque(kept, maxlen=MAX_SLOTS)

    def _slot_for_device(self, device):
        if device in self.device_slot_memory:
            slot = self.device_slot_memory[device]
            if self._slot_available(slot, device):
                return slot
        for slot, info in self.retained_off_slots.items():
            if info.get("device") == device and self._slot_available(slot, device):
                return int(slot)
        return self._first_free_slot()

    def _slot_available(self, slot, device):
        slot = int(slot)
        for item in self.active:
            if int(item.get("slot", -1)) == slot and item.get("device") != device:
                return False
        for item in self.off_events:
            if int(item.get("slot", -1)) == slot and item.get("device") != device:
                return False
        info = self.retained_off_slots.get(slot)
        if info and info.get("device") != device:
            return False
        return 0 <= slot < MAX_SLOTS

    def _first_free_slot(self):
        used = {int(x.get("slot", 0)) for x in self.active}
        used.update({int(x.get("slot", 0)) for x in self.off_events})
        used.update({int(s) for s in self.retained_off_slots.keys()})
        for i in range(MAX_SLOTS):
            if i not in used:
                return i
        return MAX_SLOTS - 1

    def _remove_off_event(self, device):
        device = normalize_device(device)
        self.off_events = deque([x for x in self.off_events if x.get("device") != device], maxlen=MAX_SLOTS)

    def _remember_retained_off(self, item):
        dev = normalize_device(item.get("device"))
        if dev is None:
            return
        slot = int(item.get("slot", 0))
        if 0 <= slot < MAX_SLOTS:
            self.retained_off_slots[slot] = {"device": dev, "conf": safe_float(item.get("conf", 0.80)), "source": item.get("source", "off_expired")}
            self.device_slot_memory[dev] = slot

    def _clear_retained_off(self, device=None, slot=None):
        device = normalize_device(device) if device is not None else None
        remove = []
        for s, info in self.retained_off_slots.items():
            if (device is not None and info.get("device") == device) or (slot is not None and int(s) == int(slot)):
                remove.append(s)
        for s in remove:
            self.retained_off_slots.pop(s, None)

    def _output(self, ai_result=None, event=None):
        states = ["EMPTY"] * MAX_SLOTS
        for item in self.active:
            slot = int(item.get("slot", 0))
            if 0 <= slot < MAX_SLOTS:
                states[slot] = f"{item['device'].upper()}_ON"
        for item in self.off_events:
            slot = int(item.get("slot", 0))
            if 0 <= slot < MAX_SLOTS and states[slot] == "EMPTY":
                states[slot] = f"{item['device'].upper()}_OFF"
        for slot, info in self.retained_off_slots.items():
            slot = int(slot)
            if 0 <= slot < MAX_SLOTS and states[slot] == "EMPTY":
                states[slot] = f"{info['device'].upper()}_OFF"
        active_texts = [s for s in states if s != "EMPTY"]
        return {
            "socket_states": states,
            "ai_text": f"🤖 AI: {' + '.join(active_texts)}" if active_texts else "🤖 AI: EMPTY",
            "active_devices": list(self.active),
            "off_events": list(self.off_events),
            "retained_off_slots": dict(self.retained_off_slots),
            "event": event,
        }


class AIEngine(DSPEngine if DSPEngine is not None else object):
    def __init__(self, spi_core, buffer_size=150, verbose=True):
        if DSPEngine is None:
            raise ImportError(f"DSPEngine/DashboardUI import 실패: {_ADAPTER_IMPORT_ERROR}")
        super().__init__(spi_core, buffer_size)
        self.ai = NILMAIExtension(verbose=verbose)
        self.tracker = DeltaMultiDeviceTracker(self.ai, verbose=verbose)
        self.ai_text = "🤖 AI: READY"
        self.socket_states = ["EMPTY"] * MAX_SLOTS

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
            self.socket_states = ["EMPTY"] * MAX_SLOTS
        return ret

    def _apply_ai_result(self, result):
        if not result or not result.get("ready", False):
            self.ai_text = "🤖 AI: READY"
            self.socket_states = ["EMPTY"] * MAX_SLOTS
            return
        out = self.tracker.update(result)
        self.socket_states = out["socket_states"][:MAX_SLOTS]
        self.ai_text = out["ai_text"]
        state = str(result.get("state", "empty")).lower()
        raw_state = str(result.get("raw_state", state)).lower()
        abs_device = normalize_device(result.get("device"))
        event = out.get("event")
        event_text = event.get("type", "?").upper() if event else "None"
        print(
            f"[AI ADAPTER] state={state} raw={raw_state} "
            f"sconf={safe_float(result.get('state_conf')):.2f} abs_device={abs_device} "
            f"dconf={safe_float(result.get('device_conf')):.2f} event={event_text} "
            f"active={self.socket_states} display={self.ai_text}"
        )


class AIDashboardUI(DashboardUI if DashboardUI is not None else object):
    def __init__(self, *args, **kwargs):
        if DashboardUI is None:
            raise ImportError(f"DSPEngine/DashboardUI import 실패: {_ADAPTER_IMPORT_ERROR}")
        super().__init__(*args, **kwargs)
        self.fig.subplots_adjust(left=0.3)
        self.fig.text(0.03, 0.9, "AI MULTITAP", color="cyan", fontsize=18, fontweight="bold")
        self.socket_texts = []
        for i in range(MAX_SLOTS):
            txt = self.fig.text(0.03, 0.7 - (i * 0.18), f"[ Slot {i + 1} ]\nEMPTY", color="gray", fontsize=15, fontweight="bold")
            self.socket_texts.append(txt)

    def update_frame(self, frame):
        artists = super().update_frame(frame)
        if hasattr(self, "engine") and hasattr(self.engine, "socket_states"):
            for i in range(MAX_SLOTS):
                state = self.engine.socket_states[i]
                color = "gray" if state == "EMPTY" else ("orange" if "OFF" in state else "lime")
                self.socket_texts[i].set_text(f"[ Slot {i + 1} ]\n{state}")
                self.socket_texts[i].set_color(color)
                if isinstance(artists, list):
                    artists.append(self.socket_texts[i])
        if hasattr(self, "ax1") and hasattr(self, "engine") and hasattr(self.engine, "ai_text"):
            curr_title = self.ax1.get_title().split("  ||  ")[0]
            self.ax1.set_title(f"{curr_title}  ||  {self.engine.ai_text}", color="yellow")
        return artists


if __name__ == "__main__":
    NILMAIExtension(verbose=True)
    print("[TEST] 모델 로드 성공")
