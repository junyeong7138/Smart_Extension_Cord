#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2_make_summary_from_raw.py  (v2)
================================
RAW CSV → Frame-level Summary CSV 생성.

v1 대비 변경점
--------------
1) frame feature 계산을 feature_extractor.extract_frame_features 로 일원화
   → 학습/추론과 동일한 FFT/통계 사용 (분포 불일치 방지)
2) clean_signal, calc_rms, _compute_harmonics 등 중복 함수 제거
   → 단일 진실 출처(feature_extractor)
3) 학습에 필수가 아닌 참고용 컬럼(Vrms_adc, Vpeak_adc 등)은 유지
   → 데이터 점검 및 디버깅 편의

유지 기능
---------
- RAW CSV 읽기, 파일명 파싱 (device/mode/run_id)
- DROP_FIRST_DUMMY_SAMPLE
- add_state_features() (baseline/delta/state/valid_for_training)
- 파일 입출력
"""

import sys
import os
import glob
import numpy as np
import pandas as pd

# 현재 파일이 있는 디렉토리의 상위 상위 경로를 시스템 패스에 추가
# RaspberryPi 폴더가 위치한 곳이 시스템 경로에 포함되어야 합니다.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 공용 feature 모듈
from Project.kwon.RaspberryPi.NILM.feature_extractor import (
    extract_frame_features,
    FRAME_FEATURE_NAMES,
)

# =====================================================================
# 1. 경로 설정 (v1과 동일)
# =====================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Data", "RAW"))
SUMMARY_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Data", "SUMMARY"))
os.makedirs(SUMMARY_DIR, exist_ok=True)

# =====================================================================
# 2. 전처리 설정
# =====================================================================
BASELINE_FRAMES = 10
DELTA_SMOOTH_WINDOW = 3

# state 판정 임계값 (P_proxy 스케일)
MIN_THRESHOLD_I = 10.0
MIN_THRESHOLD_PABS = 3000.0
MIN_THRESHOLD_H1 = 1.0

THRESHOLD_SIGMA_I = 3.0
THRESHOLD_SIGMA_PABS = 3.0
THRESHOLD_SIGMA_H1 = 3.0

OFF_RATIO = 0.6
TRANSIENT_MARGIN_FRAMES = 1

DROP_FIRST_DUMMY_SAMPLE = True

EPS = 1e-9


# =====================================================================
# 3. 유틸 함수
# =====================================================================

def safe_num_series(s):
    return pd.to_numeric(s, errors="coerce")


def calc_fs_from_timestamps(timestamps):
    timestamps = np.asarray(timestamps, dtype=np.float64)
    if len(timestamps) < 2:
        return 0.0
    dt = np.diff(timestamps)
    dt = dt[dt > 0]
    if len(dt) == 0:
        return 0.0
    return float(1.0 / np.mean(dt))


def moving_average(s, window):
    return s.rolling(window=window, min_periods=1).mean()


def first_valid_value(df, col, default="unknown"):
    if col in df.columns and df[col].notna().any():
        return str(df[col].dropna().iloc[0])
    return default


def infer_device_mode_runid(df, file_path):
    """
    우선 CSV 컬럼의 device/mode/run_id를 사용.
    없으면 파일명에서 최대한 추정.
    """
    run_id = first_valid_value(df, "run_id", "unknown")
    device = first_valid_value(df, "device", "unknown").lower()
    mode = first_valid_value(df, "mode", "UNKNOWN").upper()

    if device != "unknown" and mode != "UNKNOWN":
        return run_id, device, mode

    base = os.path.basename(file_path)
    name = os.path.splitext(base)[0]
    parts = name.split("_")

    if len(parts) >= 4 and parts[0].lower() == "raw":
        try:
            time_idx = parts.index("time")
        except ValueError:
            time_idx = -1

        if time_idx > 1:
            middle = parts[1:time_idx]
            known_devices = ["charger", "microwave", "tv", "dryer", "cleaner"]

            detected_devices = []
            rest_start = 0
            for idx, p in enumerate(middle):
                if p.lower() in known_devices:
                    detected_devices.append(p.lower())
                    rest_start = idx + 1
                else:
                    break

            if detected_devices:
                device = "_".join(detected_devices)
                mode_parts = middle[rest_start:]
                mode = "_".join(mode_parts).upper() if mode_parts else "ON"
            else:
                device = middle[0].lower()
                mode = "_".join(middle[1:]).upper() if len(middle) > 1 else "ON"

            run_id = "_".join(parts[time_idx + 1:]) if len(parts) > time_idx + 1 else run_id

    return run_id, device, mode


def find_time_raw_files():
    """우선 raw_*_time_*.csv. 없으면 raw_*.csv 중 fft 제외."""
    time_files = sorted(glob.glob(os.path.join(RAW_DIR, "raw_*_time_*.csv")))
    if time_files:
        return time_files
    all_files = sorted(glob.glob(os.path.join(RAW_DIR, "raw_*.csv")))
    return [f for f in all_files if "_fft_" not in os.path.basename(f).lower()]


# =====================================================================
# 4. Frame 단위 feature 계산 (feature_extractor에 위임)
# =====================================================================

def extract_features_one_frame(g):
    """
    하나의 frame_index 그룹에서 frame-level feature 추출.

    핵심 10개 feature는 feature_extractor.extract_frame_features 사용 (학습/추론과 일치).
    참고용 메타 컬럼(Vrms_adc, Vpeak_adc, time, n_samples 등)도 함께 반환.
    """
    g = g.sort_values("sample_or_bin_index").copy()

    ch0 = safe_num_series(g["ch0_adc_centered"]).dropna().values
    ch1 = safe_num_series(g["ch1_adc_centered"]).dropna().values
    ts = safe_num_series(g["timestamp"]).dropna().values

    n = min(len(ch0), len(ch1), len(ts))
    if n < 10:
        return None

    ch0 = ch0[:n]
    ch1 = ch1[:n]
    ts = ts[:n]

    # fs 계산 (수집 시 기록된 fs_actual 우선, 없으면 timestamp로)
    if "fs_actual" in g.columns and g["fs_actual"].notna().any():
        fs_actual = float(safe_num_series(g["fs_actual"]).dropna().iloc[0])
    else:
        fs_actual = calc_fs_from_timestamps(ts)

    # === 핵심: 학습/추론과 동일한 feature ===
    core_feat = extract_frame_features(ch0, ch1, fs_actual)

    # === 참고용 메타 컬럼 (학습엔 직접 사용 안 함) ===
    # Vrms_adc, Vpeak_adc, Ipeak 등은 디버깅/시각화 편의용
    ch0_arr = np.asarray(ch0, dtype=np.float64)
    ch1_arr = np.asarray(ch1, dtype=np.float64)
    vrms = float(np.sqrt(np.mean(ch0_arr ** 2))) if len(ch0_arr) > 0 else 0.0
    vpeak = float(np.max(np.abs(ch0_arr))) if len(ch0_arr) > 0 else 0.0
    ipeak = float(np.max(np.abs(ch1_arr))) if len(ch1_arr) > 0 else 0.0
    vpp = float(np.max(ch0_arr) - np.min(ch0_arr)) if len(ch0_arr) > 0 else 0.0
    ipp = float(np.max(ch1_arr) - np.min(ch1_arr)) if len(ch1_arr) > 0 else 0.0

    out = {
        "time": float(ts[0]),
        "n_samples": int(n),
        "fs_actual": round(float(fs_actual), 3),

        # 참고용 (학습 사용 X)
        "Vrms_adc": round(vrms, 6),
        "Vpeak_adc": round(vpeak, 6),
        "Vpp_adc": round(vpp, 6),
        "Ipeak_adc": round(ipeak, 6),
        "Ipp_adc": round(ipp, 6),
    }

    # 핵심 10개 (학습 사용 O) - 컬럼명 그대로
    for k in FRAME_FEATURE_NAMES:
        out[k] = round(float(core_feat[k]), 6)

    return out


# =====================================================================
# 5. RAW → frame summary
# =====================================================================

def build_frame_summary(raw_file):
    df = pd.read_csv(raw_file)

    required = [
        "record_type", "frame_index", "sample_or_bin_index",
        "timestamp", "ch0_adc_centered", "ch1_adc_centered",
    ]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"'{col}' 컬럼 없음")

    df = df[df["record_type"].astype(str).str.lower() == "time"].copy()
    if df.empty:
        raise ValueError("record_type=time 데이터 없음")

    if DROP_FIRST_DUMMY_SAMPLE:
        df = df[
            ~(
                (safe_num_series(df["frame_index"]) == 0)
                & (safe_num_series(df["sample_or_bin_index"]) == 0)
            )
        ].copy()

    run_id, device, mode = infer_device_mode_runid(df, raw_file)

    df["frame_index"] = safe_num_series(df["frame_index"]).astype(int)
    df["sample_or_bin_index"] = safe_num_series(df["sample_or_bin_index"]).astype(int)

    rows = []
    for frame_idx, g in df.groupby("frame_index"):
        feat = extract_features_one_frame(g)
        if feat is None:
            continue

        feat.update({
            "run_id": run_id,
            "device": device,
            "mode": mode,
            "source_raw_file": os.path.basename(raw_file),
            "frame_index": int(frame_idx),
        })
        rows.append(feat)

    if not rows:
        raise ValueError("frame summary 생성 결과가 비어 있음")

    out = pd.DataFrame(rows)
    out = out.sort_values("frame_index").reset_index(drop=True)
    out["elapsed_s"] = out["time"] - out["time"].iloc[0]

    # 컬럼 순서 정리
    front_cols = [
        "run_id", "device", "mode", "source_raw_file",
        "frame_index", "time", "elapsed_s",
        "n_samples", "fs_actual",
    ]
    other_cols = [c for c in out.columns if c not in front_cols]
    out = out[front_cols + other_cols]

    return out


# =====================================================================
# 6. baseline / delta / state / valid_for_training 추가 (v1 그대로 유지)
# =====================================================================

def add_state_features(summary):
    df = summary.copy()

    if len(df) < BASELINE_FRAMES:
        raise ValueError(f"baseline frame 부족: {len(df)} < {BASELINE_FRAMES}")

    baseline = df.head(BASELINE_FRAMES)

    baseline_irms = float(baseline["Irms_adc"].mean())
    baseline_p = float(baseline["P_proxy"].mean())
    baseline_pabs = float(baseline["Pabs_mean_proxy"].mean())
    baseline_h1 = float(baseline["H1_60_mag"].mean())
    baseline_thd = float(baseline["THD_i"].mean())
    baseline_crest = float(baseline["crest_factor_i"].mean())

    noise_i = float(baseline["Irms_adc"].std(ddof=0))
    noise_pabs = float(baseline["Pabs_mean_proxy"].std(ddof=0))
    noise_h1 = float(baseline["H1_60_mag"].std(ddof=0))

    thr_i = max(noise_i * THRESHOLD_SIGMA_I, MIN_THRESHOLD_I)
    thr_pabs = max(noise_pabs * THRESHOLD_SIGMA_PABS, MIN_THRESHOLD_PABS)
    thr_h1 = max(noise_h1 * THRESHOLD_SIGMA_H1, MIN_THRESHOLD_H1)

    df["baseline_Irms_adc"] = baseline_irms
    df["baseline_P_proxy"] = baseline_p
    df["baseline_Pabs_mean_proxy"] = baseline_pabs
    df["baseline_H1_60_mag"] = baseline_h1
    df["baseline_THD_i"] = baseline_thd
    df["baseline_crest_factor_i"] = baseline_crest

    df["delta_Irms_adc"] = df["Irms_adc"] - baseline_irms
    df["delta_P_proxy"] = df["P_proxy"] - baseline_p
    df["delta_Pabs_mean_proxy"] = df["Pabs_mean_proxy"] - baseline_pabs
    df["delta_H1_60_mag"] = df["H1_60_mag"] - baseline_h1
    df["delta_THD_i"] = df["THD_i"] - baseline_thd
    df["delta_crest_factor_i"] = df["crest_factor_i"] - baseline_crest

    df["delta_Irms_adc_avg"] = moving_average(df["delta_Irms_adc"], DELTA_SMOOTH_WINDOW)
    df["delta_P_proxy_avg"] = moving_average(df["delta_P_proxy"], DELTA_SMOOTH_WINDOW)
    df["delta_Pabs_mean_proxy_avg"] = moving_average(df["delta_Pabs_mean_proxy"], DELTA_SMOOTH_WINDOW)
    df["delta_H1_60_mag_avg"] = moving_average(df["delta_H1_60_mag"], DELTA_SMOOTH_WINDOW)
    df["delta_THD_i_avg"] = moving_average(df["delta_THD_i"], DELTA_SMOOTH_WINDOW)
    df["delta_crest_factor_i_avg"] = moving_average(df["delta_crest_factor_i"], DELTA_SMOOTH_WINDOW)

    df["thr_Irms_adc"] = round(thr_i, 6)
    df["thr_Pabs_mean_proxy"] = round(thr_pabs, 6)
    df["thr_H1_60_mag"] = round(thr_h1, 6)

    states = []
    prev_state = "OFF"

    for _, row in df.iterrows():
        di = abs(float(row["delta_Irms_adc_avg"]))
        dpabs = abs(float(row["delta_Pabs_mean_proxy_avg"]))
        dh1 = abs(float(row["delta_H1_60_mag_avg"]))

        if prev_state == "OFF":
            if (di >= thr_i) or (dpabs >= thr_pabs) or (dh1 >= thr_h1):
                state = "ON"
            else:
                state = "OFF"
        else:
            if (
                (di <= thr_i * OFF_RATIO)
                and (dpabs <= thr_pabs * OFF_RATIO)
                and (dh1 <= thr_h1 * OFF_RATIO)
            ):
                state = "OFF"
            else:
                state = "ON"

        states.append(state)
        prev_state = state

    df["state"] = states
    df["auto_level"] = np.where(df["state"] == "ON", df["mode"], "OFF")

    df["is_transient"] = False
    state_changed = df["state"] != df["state"].shift(1)

    for idx in df.index[state_changed]:
        start = max(0, idx - TRANSIENT_MARGIN_FRAMES)
        end = min(len(df) - 1, idx + TRANSIENT_MARGIN_FRAMES)
        df.loc[start:end, "is_transient"] = True

    if len(df) > 0:
        df.loc[0, "is_transient"] = False

    df["valid_for_training"] = (df["state"] == "ON") & (~df["is_transient"])

    return df


# =====================================================================
# 7. 파일 처리
# =====================================================================

def process_one_file(raw_file):
    print(f"\n[PROCESS] {os.path.basename(raw_file)}")

    frame_summary = build_frame_summary(raw_file)
    final_summary = add_state_features(frame_summary)

    run_id = str(final_summary["run_id"].iloc[0])
    device = str(final_summary["device"].iloc[0])
    mode = str(final_summary["mode"].iloc[0])

    out_name = f"summary_{device}_{mode}_{run_id}.csv"
    out_path = os.path.join(SUMMARY_DIR, out_name)

    final_summary.to_csv(out_path, index=False)

    print(f"[SAVE] {out_path}")
    print(f"       rows={len(final_summary)}")
    print(f"       ON frames={(final_summary['state'] == 'ON').sum()}")
    print(f"       valid_for_training={final_summary['valid_for_training'].sum()}")
    print(f"       baseline_Pabs={final_summary['baseline_Pabs_mean_proxy'].iloc[0]:.2f}")
    print(f"       thr_Pabs={final_summary['thr_Pabs_mean_proxy'].iloc[0]:.2f}")

    return out_path


# =====================================================================
# 8. main
# =====================================================================

def main():
    raw_files = find_time_raw_files()

    print("=== NILM RAW → SUMMARY 생성 (v2) ===")
    print("RAW_DIR     =", RAW_DIR)
    print("SUMMARY_DIR =", SUMMARY_DIR)
    print("raw 개수    =", len(raw_files))

    if not raw_files:
        print("[INFO] raw 파일이 없음")
        return

    out_files = []
    for raw_file in raw_files:
        try:
            out_files.append(process_one_file(raw_file))
        except Exception as e:
            print(f"[ERROR] {os.path.basename(raw_file)} 처리 실패: {e}")

    print("\n=== 완료 ===")
    print(f"summary 생성 개수: {len(out_files)}")


if __name__ == "__main__":
    main()
