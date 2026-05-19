#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import numpy as np
import pandas as pd

# =========================================================
# 1. 경로 설정 (사용자 요구사항 반영)
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 참조 경로 1: 실제 수집 데이터 (../../once)
ONCE_RAW_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "once"))

# 참조 경로 2: 합성 데이터 (../../Data/Fake_Multi_Raw)
FAKE_RAW_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Data", "Fake_Multi_Raw"))

# 결과 저장 경로: 프로젝트 통합 SUMMARY 폴더 (../../Data/SUMMARY)
SUMMARY_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Data", "SUMMARY"))
os.makedirs(SUMMARY_DIR, exist_ok=True)

# 탐색할 폴더 리스트
RAW_DIRS = [ONCE_RAW_DIR, FAKE_RAW_DIR]

# =========================================================
# 2. 전처리 설정
# =========================================================
BASELINE_FRAMES = 10
DELTA_SMOOTH_WINDOW = 3
THRESHOLD_SIGMA_I = 3.0
THRESHOLD_SIGMA_P = 3.0
MIN_THRESHOLD_I = 20.0
MIN_THRESHOLD_P = 5000.0
OFF_RATIO = 0.6
TRANSIENT_MARGIN_FRAMES = 1
DROP_FIRST_DUMMY_SAMPLE = True
EPS = 1e-9

def infer_meta_from_df(df, file_path):
    run_id = str(df["run_id"].dropna().iloc[0]) if "run_id" in df.columns else "unknown"
    device = str(df["device"].dropna().iloc[0]) if "device" in df.columns else "unknown"
    mode = str(df["mode"].dropna().iloc[0]) if "mode" in df.columns else "unknown"
    return run_id, device, mode

def clean_signal(x):
    x = np.asarray(x, dtype=np.float64)
    if len(x) == 0: return x
    lo, hi = np.percentile(x, 1), np.percentile(x, 99)
    return np.clip(x, lo, hi) if lo < hi else x

def build_time_summary(time_csv_path):
    df = pd.read_csv(time_csv_path)
    df = df[df["record_type"].astype(str) == "time"].copy()
    
    if DROP_FIRST_DUMMY_SAMPLE:
        df = df[~((df["frame_index"] == 0) & (df["sample_or_bin_index"] == 0))].copy()

    run_id, device, mode = infer_meta_from_df(df, time_csv_path)
    rows = []

    for frame_idx, g in df.groupby("frame_index"):
        g = g.sort_values("sample_or_bin_index").copy()
        t = pd.to_numeric(g["timestamp"], errors="coerce").dropna().values
        ch0 = pd.to_numeric(g["ch0_adc_centered"], errors="coerce").dropna().values
        ch1 = pd.to_numeric(g["ch1_adc_centered"], errors="coerce").dropna().values
        n = min(len(ch0), len(ch1), len(t))
        if n < 10: continue

        ch0_c = clean_signal(ch0[:n])
        ch1_c = clean_signal(ch1[:n])
        t = t[:n]
        p_inst = ch0_c * ch1_c

        vrms_adc, irms_adc = float(np.sqrt(np.mean(ch0_c**2))), float(np.sqrt(np.mean(ch1_c**2)))
        ipeak = float(np.max(np.abs(ch1_c)))
        fs_actual = float(g["fs_actual"].dropna().iloc[0]) if "fs_actual" in g.columns else 1920.0

        # 실전(ai_extension.py)과 동일한 Python FFT 추출
        x = ch1_c - np.mean(ch1_c)
        if len(x) >= 8 and fs_actual > 0:
            xw = x * np.hanning(len(x))
            mags = np.abs(np.fft.rfft(xw))
            freqs = np.fft.rfftfreq(len(xw), d=1.0 / fs_actual)

            def get_mag(target_freq):
                if len(freqs) == 0: return 0.0
                return float(mags[np.argmin(np.abs(freqs - target_freq))])

            h1, h3, h5, h7 = get_mag(60.0), get_mag(180.0), get_mag(300.0), get_mag(420.0)
            thd_i = float(np.sqrt(h3 ** 2 + h5 ** 2 + h7 ** 2) / h1) if h1 > EPS else 0.0
            
            valid = freqs >= 60.0
            if np.any(valid):
                peak_idx = int(np.argmax(mags[valid]))
                peak_freq, peak_mag = float(freqs[valid][peak_idx]), float(mags[valid][peak_idx])
            else:
                peak_freq, peak_mag = 0.0, 0.0
        else:
            h1 = h3 = h5 = h7 = thd_i = peak_freq = peak_mag = 0.0

        rows.append({
            "run_id": run_id, "device": device, "mode": mode,
            "source_time_file": os.path.basename(time_csv_path),
            "frame_index": int(frame_idx), "time": float(t[0]), "n_samples": int(n), "fs_actual": fs_actual,
            "Vrms_adc": vrms_adc, "Irms_adc": irms_adc, "P_proxy": float(np.mean(p_inst)),
            "H1_60_mag": h1, "H3_180_mag": h3, "H5_300_mag": h5, "H7_420_mag": h7, "THD_i": thd_i,
            "fft_peak_freq": peak_freq, "fft_peak_mag": peak_mag
        })

    out = pd.DataFrame(rows).sort_values("frame_index").reset_index(drop=True)
    return out

def add_state_features(df):
    baseline_part = df.head(BASELINE_FRAMES)
    b_irms, b_p = float(baseline_part["Irms_adc"].mean()), float(baseline_part["P_proxy"].mean())
    thr_i = max(float(baseline_part["Irms_adc"].std(ddof=0)) * THRESHOLD_SIGMA_I, MIN_THRESHOLD_I)
    thr_p = max(float(baseline_part["P_proxy"].std(ddof=0)) * THRESHOLD_SIGMA_P, MIN_THRESHOLD_P)

    df["baseline_Irms_adc"], df["baseline_P_proxy"] = b_irms, b_p
    df["delta_Irms_adc"], df["delta_P_proxy"] = df["Irms_adc"] - b_irms, df["P_proxy"] - b_p
    df["delta_Irms_adc_avg"] = df["delta_Irms_adc"].rolling(window=DELTA_SMOOTH_WINDOW, min_periods=1).mean()
    df["delta_P_proxy_avg"] = df["delta_P_proxy"].rolling(window=DELTA_SMOOTH_WINDOW, min_periods=1).mean()

    states, prev_state = [], "OFF"
    for _, row in df.iterrows():
        di, dp = abs(float(row["delta_Irms_adc_avg"])), abs(float(row["delta_P_proxy_avg"]))
        if prev_state == "OFF": state = "ON" if (di >= thr_i) or (dp >= thr_p) else "OFF"
        else: state = "OFF" if (di <= thr_i * OFF_RATIO) and (dp <= thr_p * OFF_RATIO) else "ON"
        states.append(state)
        prev_state = state

    df["state"] = states
    df["valid_for_training"] = (df["state"] == "ON")
    df["thr_Irms_adc"], df["thr_P_proxy"] = thr_i, thr_p
    return df

def main():
    all_time_files = []
    for raw_dir in RAW_DIRS:
        if not os.path.exists(raw_dir):
            print(f"⚠️ 경로 없음: {raw_dir}")
            continue
        pattern = os.path.join(raw_dir, "raw_*_time_*.csv")
        files = glob.glob(pattern)
        all_time_files.extend(files)
        print(f"📂 폴더 스캔: {raw_dir} (발견: {len(files)}개)")

    if not all_time_files:
        print("⚠️ 처리할 RAW 파일이 없습니다.")
        return

    print(f"🚀 총 {len(all_time_files)}개 파일 전처리 시작...")
    
    for time_file in sorted(all_time_files):
        try:
            summary = add_state_features(build_time_summary(time_file))
            fname = f"summary_{summary['device'].iloc[0]}_{summary['mode'].iloc[0]}_{summary['run_id'].iloc[0]}.csv"
            summary.to_csv(os.path.join(SUMMARY_DIR, fname), index=False)
            print(f"✅ [완료] {fname}")
        except Exception as e:
            print(f"❌ [에러] {os.path.basename(time_file)}: {e}")

if __name__ == "__main__":
    main()