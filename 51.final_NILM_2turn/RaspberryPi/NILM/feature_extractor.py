#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
feature_extractor.py
====================
NILM 시스템 전체에서 사용하는 통합 feature 추출 모듈.

학습 / 전처리 / 추론 코드가 모두 이 모듈을 import해서
동일한 feature를 생성하도록 강제한다. (학습-추론 분포 불일치 방지)

API:
    extract_frame_features(ch0, ch1, fs_actual) -> dict
        한 frame(약 150 sample)에서 frame-level feature 14종 추출.

    aggregate_window_features(frame_dicts) -> dict
        N(=WINDOW_SIZE)개의 frame feature를 mean/std로 묶어
        window-level feature 28종(14 mean + 14 std) 생성.

    FRAME_FEATURE_NAMES  : frame feature 컬럼 순서 (14개)
    WINDOW_FEATURE_NAMES : window feature 컬럼 순서 (28개)
                          → RF 모델의 입력 컬럼 순서와 일치해야 함

주의:
    - P_proxy / Q_proxy / S_proxy 는 ADC raw (centered) 곱이라 W/VA/VAR 가 아니다.
      변수명에 _proxy 를 붙여 ADC unit 임을 표시. 학습/추론은 동일한 단위라 무관.
    - PF_proxy 는 dimensionless 이므로 ADC 무관, 위상 정보를 직접 담는다.

NILM 표준 4대 전력 feature (Hart 1992 이래 표준):
    P (유효전력) : mean(v·i)         → P_proxy
    S (피상전력) : Vrms · Irms        → S_proxy
    Q (무효전력) : sqrt(S² - P²)      → Q_proxy
    PF (역률)    : P/S = cos(φ)       → PF_proxy
"""

import numpy as np
import pandas as pd

# =====================================================================
# 설정
# =====================================================================

# Window aggregation 크기 (frame 개수)
WINDOW_SIZE = 10

# Percentile clip (ADC raw 스파이크 방어)
CLIP_LOW_PCT = 1
CLIP_HIGH_PCT = 99
USE_PERCENTILE_CLIP = True

# FFT 대상 고조파 주파수
HARMONIC_FREQS = {
    "H1_60_mag":  60.0,
    "H3_180_mag": 180.0,
    "H5_300_mag": 300.0,
    "H7_420_mag": 420.0,
}

# 수치 안정성
EPS = 1e-9

# Frame-level feature 컬럼 순서 (학습 코드 cols와 100% 일치 필수)
# 기존 10개 뒤에 새 4개를 append. 인덱스 변경 없음 → ai_extension_v3 호환 유지.
FRAME_FEATURE_NAMES = [
    "Irms_adc",
    "P_proxy",
    "Pabs_mean_proxy",
    "Pstd_proxy",
    "crest_factor_i",
    "H1_60_mag",
    "H3_180_mag",
    "H5_300_mag",
    "H7_420_mag",
    "THD_i",
    # --- v2: NILM 표준 4대 전력 feature (Vrms 포함) ---
    "Vrms_adc",
    "S_proxy",
    "Q_proxy",
    "PF_proxy",
]

# Window-level feature 컬럼 순서 (각 frame feature의 mean / std)
# RF 모델 입력 순서와 정확히 일치해야 함
WINDOW_FEATURE_NAMES = []
for _name in FRAME_FEATURE_NAMES:
    WINDOW_FEATURE_NAMES.append(f"{_name}_mean")
    WINDOW_FEATURE_NAMES.append(f"{_name}_std")


# =====================================================================
# 내부 유틸
# =====================================================================

def _clean_signal(x):
    """1~99 percentile clip으로 ADC 스파이크 제거."""
    x = np.asarray(x, dtype=np.float64)
    if len(x) == 0 or not USE_PERCENTILE_CLIP:
        return x
    lo = np.percentile(x, CLIP_LOW_PCT)
    hi = np.percentile(x, CLIP_HIGH_PCT)
    if lo >= hi:
        return x
    return np.clip(x, lo, hi)


def _rms(x):
    if len(x) == 0:
        return 0.0
    return float(np.sqrt(np.mean(x ** 2)))


def _compute_harmonics(ch1_clipped, fs_actual):
    """
    ch1 전류 파형에서 60/180/300/420 Hz 고조파 크기와 THD 계산.

    - FFT 길이: 입력 그대로 (frame당 약 150 sample)
    - Window: Hanning
    - DC 제거: 평균 빼기
    - bin lookup: fs_actual 기반 동적 (rfftfreq에서 가장 가까운 bin)

    학습 코드(2_make_summary_from_raw.py)와 동일한 방식.
    """
    out = {"H1_60_mag": 0.0, "H3_180_mag": 0.0,
           "H5_300_mag": 0.0, "H7_420_mag": 0.0,
           "THD_i": 0.0}

    n = len(ch1_clipped)
    if n <= 16 or fs_actual <= 0:
        return out

    x = ch1_clipped - np.mean(ch1_clipped)
    xw = x * np.hanning(n)

    mags = np.abs(np.fft.rfft(xw))
    freqs = np.fft.rfftfreq(n, d=1.0 / fs_actual)

    if len(freqs) == 0:
        return out

    def get_mag(target_hz):
        idx = int(np.argmin(np.abs(freqs - target_hz)))
        return float(mags[idx])

    h1 = get_mag(60.0)
    h3 = get_mag(180.0)
    h5 = get_mag(300.0)
    h7 = get_mag(420.0)

    out["H1_60_mag"] = h1
    out["H3_180_mag"] = h3
    out["H5_300_mag"] = h5
    out["H7_420_mag"] = h7

    if h1 > EPS:
        out["THD_i"] = float(np.sqrt(h3 ** 2 + h5 ** 2 + h7 ** 2) / h1)

    return out


# =====================================================================
# 공개 API
# =====================================================================

def extract_frame_features(ch0, ch1, fs_actual):
    """
    한 frame(약 150 sample)의 ch0(전압), ch1(전류) raw ADC centered 데이터에서
    frame-level feature 10종을 추출.

    Parameters
    ----------
    ch0 : array-like (int or float)
        Voltage ADC centered (-2048 ~ +2047 범위)
    ch1 : array-like
        Current ADC centered
    fs_actual : float
        timestamp 기반 실측 sampling frequency (Hz)

    Returns
    -------
    dict
        FRAME_FEATURE_NAMES 순서대로 정렬된 10개 feature.
        모든 값은 float.
    """
    ch0 = np.asarray(ch0, dtype=np.float64)
    ch1 = np.asarray(ch1, dtype=np.float64)

    # 길이 정렬
    n = min(len(ch0), len(ch1))
    if n < 10:
        # 너무 짧으면 0으로 채운 dict 반환
        return {k: 0.0 for k in FRAME_FEATURE_NAMES}
    ch0 = ch0[:n]
    ch1 = ch1[:n]

    # Outlier clip
    ch0 = _clean_signal(ch0)
    ch1 = _clean_signal(ch1)

    # 기본 통계
    vrms = _rms(ch0)
    irms = _rms(ch1)
    ipeak = float(np.max(np.abs(ch1))) if len(ch1) > 0 else 0.0
    crest_factor_i = float(ipeak / irms) if irms > EPS else 0.0

    # P proxy 계열 (ADC raw 단위, W 아님)
    p_inst = ch0 * ch1
    p_proxy = float(np.mean(p_inst))
    pabs_mean_proxy = float(np.mean(np.abs(p_inst)))
    pstd_proxy = float(np.std(p_inst))

    # NILM 표준 4대 전력 feature (ADC 단위 근사)
    # S = Vrms·Irms (피상전력), Q = sqrt(S²-P²) (무효전력), PF = P/S (역률)
    # 부호 보존: P_proxy가 음수일 수 있으면 PF도 음수 가능 (위상 >90도).
    # max(., 0) 으로 sqrt 음수 방지 (수치 노이즈로 P²>S² 인 edge case 차단).
    s_proxy = vrms * irms
    q_proxy = float(np.sqrt(max(s_proxy * s_proxy - p_proxy * p_proxy, 0.0)))
    pf_proxy = float(p_proxy / s_proxy) if s_proxy > EPS else 0.0

    # Harmonic + THD (ch1 기준)
    harmonics = _compute_harmonics(ch1, fs_actual)

    feat = {
        "Irms_adc": irms,
        "P_proxy": p_proxy,
        "Pabs_mean_proxy": pabs_mean_proxy,
        "Pstd_proxy": pstd_proxy,
        "crest_factor_i": crest_factor_i,
        "H1_60_mag": harmonics["H1_60_mag"],
        "H3_180_mag": harmonics["H3_180_mag"],
        "H5_300_mag": harmonics["H5_300_mag"],
        "H7_420_mag": harmonics["H7_420_mag"],
        "THD_i": harmonics["THD_i"],
        "Vrms_adc": vrms,
        "S_proxy": s_proxy,
        "Q_proxy": q_proxy,
        "PF_proxy": pf_proxy,
    }

    # 순서 보장 (dict 순서가 깨지지 않게 명시적으로 다시 만듦)
    return {k: float(feat[k]) for k in FRAME_FEATURE_NAMES}


def aggregate_window_features(frame_dicts):
    """
    N개의 frame feature dict 리스트를 받아 window-level feature dict로 집계.

    Parameters
    ----------
    frame_dicts : list of dict
        각 dict는 extract_frame_features의 반환값.
        길이는 WINDOW_SIZE에 가까운 것을 권장 (정확히 같을 필요는 없음).

    Returns
    -------
    dict
        WINDOW_FEATURE_NAMES 순서대로 정렬된 20개 feature (각 mean/std).
        std는 ddof=0 (모집단 표준편차).
    """
    if len(frame_dicts) == 0:
        return {k: 0.0 for k in WINDOW_FEATURE_NAMES}

    df = pd.DataFrame(frame_dicts)

    win = {}
    for name in FRAME_FEATURE_NAMES:
        if name in df.columns:
            s = df[name].astype(float)
            win[f"{name}_mean"] = float(s.mean())
            win[f"{name}_std"] = float(s.std(ddof=0))
        else:
            win[f"{name}_mean"] = 0.0
            win[f"{name}_std"] = 0.0

    # 순서 보장
    return {k: float(win[k]) for k in WINDOW_FEATURE_NAMES}


# =====================================================================
# Self-test (모듈 단독 실행 시)
# =====================================================================

if __name__ == "__main__":
    # 합성 신호: 60Hz 정현파 + 3차/5차 고조파
    fs = 1920.0
    n = 150
    t = np.arange(n) / fs

    v = (2000 * np.sin(2 * np.pi * 60 * t)).astype(np.int64)
    i = (
        100 * np.sin(2 * np.pi * 60 * t)
        + 30 * np.sin(2 * np.pi * 180 * t)
        + 15 * np.sin(2 * np.pi * 300 * t)
    ).astype(np.int64)

    feat = extract_frame_features(v, i, fs)
    print("=== Frame feature ===")
    for k, v_ in feat.items():
        print(f"  {k:20s} = {v_:12.3f}")

    # window aggregation 테스트
    frames = [extract_frame_features(v, i, fs) for _ in range(WINDOW_SIZE)]
    win = aggregate_window_features(frames)
    print("\n=== Window feature ===")
    for k in WINDOW_FEATURE_NAMES:
        print(f"  {k:30s} = {win[k]:12.3f}")

    print(f"\nFRAME_FEATURE_NAMES  ({len(FRAME_FEATURE_NAMES)}): {FRAME_FEATURE_NAMES}")
    print(f"WINDOW_FEATURE_NAMES ({len(WINDOW_FEATURE_NAMES)}): {WINDOW_FEATURE_NAMES}")