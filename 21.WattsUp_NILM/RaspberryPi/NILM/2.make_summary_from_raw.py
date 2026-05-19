#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import re
import numpy as np
import pandas as pd

# =========================================================
# 1. 설정
# =========================================================

# 현재 코드가 실행되는 위치 (스크립트 폴더)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 📂 RAW 파일 읽는 경로: ../../Data/RAW
RAW_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Data", "RAW"))

# 💾 Summary 파일 저장 경로: ../../Data/SUMMARY
SUMMARY_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Data", "SUMMARY"))
os.makedirs(SUMMARY_DIR, exist_ok=True)

# RAW 파일 탐색 패턴 적용
TIME_PATTERN = os.path.join(RAW_DIR, "raw_*_time_*.csv")
FFT_PATTERN = os.path.join(RAW_DIR, "raw_*_fft_*.csv")

# 초기 OFF baseline으로 사용할 프레임 수
BASELINE_FRAMES = 10

# delta smoothing window
DELTA_SMOOTH_WINDOW = 3

# 동적 threshold 설정
THRESHOLD_SIGMA_I = 3.0
THRESHOLD_SIGMA_P = 3.0

# 최소 threshold
MIN_THRESHOLD_I = 20.0
MIN_THRESHOLD_P = 5000.0

# OFF 복귀 threshold 비율
OFF_RATIO = 0.6

# 과도 구간 제거용
TRANSIENT_MARGIN_FRAMES = 1

# 첫 샘플 더미 제거 여부
DROP_FIRST_DUMMY_SAMPLE = True

# 이상치 클리핑 여부
USE_PERCENTILE_CLIP = True
CLIP_LOW_PCT = 1
CLIP_HIGH_PCT = 99

# FFT 주요 주파수
TARGET_FREQS = {
    "H1_60_mag": 60.0,
    "H3_180_mag": 180.0,
    "H5_300_mag": 300.0,
    "H7_420_mag": 420.0,
}

EPS = 1e-9

# =========================================================
# 2. 공통 함수
# =========================================================

def safe_float(x, default=np.nan):
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


def infer_meta_from_df(df, fallback_file):
    """
    CSV 내부에서 device/mode/run_id 추출
    """
    run_id = str(df["run_id"].dropna().iloc[0]) if "run_id" in df.columns and df["run_id"].notna().any() else "unknown"
    device = str(df["device"].dropna().iloc[0]) if "device" in df.columns and df["device"].notna().any() else "unknown"
    mode = str(df["mode"].dropna().iloc[0]) if "mode" in df.columns and df["mode"].notna().any() else "unknown"

    return run_id, device, mode


def clean_signal(x):
    """
    이상치 완화용 percentile clipping
    """
    x = np.asarray(x, dtype=np.float64)

    if len(x) == 0:
        return x

    if not USE_PERCENTILE_CLIP:
        return x

    lo = np.percentile(x, CLIP_LOW_PCT)
    hi = np.percentile(x, CLIP_HIGH_PCT)

    if lo >= hi:
        return x

    return np.clip(x, lo, hi)


def rms(x):
    x = np.asarray(x, dtype=np.float64)
    if len(x) == 0:
        return 0.0
    return float(np.sqrt(np.mean(x ** 2)))


def p2p(x):
    x = np.asarray(x, dtype=np.float64)
    if len(x) == 0:
        return 0.0
    return float(np.max(x) - np.min(x))


def calc_fs_from_timestamps(timestamps):
    timestamps = np.asarray(timestamps, dtype=np.float64)
    dt = np.diff(timestamps)
    dt = dt[dt > 0]

    if len(dt) == 0:
        return 0.0

    return float(1.0 / np.mean(dt))


def moving_average_series(s, window):
    return s.rolling(window=window, min_periods=1).mean()


def get_nearest_fft_value(frame_df, target_freq):
    """
    특정 target_freq에 가장 가까운 FFT magnitude 반환
    """
    if frame_df.empty:
        return np.nan

    freq = pd.to_numeric(frame_df["frequency_hz"], errors="coerce")
    mag = pd.to_numeric(frame_df["fft_magnitude"], errors="coerce")

    valid = ~(freq.isna() | mag.isna())
    freq = freq[valid]
    mag = mag[valid]

    if len(freq) == 0:
        return np.nan

    idx = (freq - target_freq).abs().idxmin()
    return float(mag.loc[idx])


# =========================================================
# 3. Time RAW → time summary
# =========================================================

def build_time_summary(time_csv_path):
    df = pd.read_csv(time_csv_path)

    required_cols = [
        "run_id",
        "device",
        "mode",
        "record_type",
        "frame_index",
        "sample_or_bin_index",
        "timestamp",
        "ch0_adc_centered",
        "ch1_adc_centered",
    ]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"{os.path.basename(time_csv_path)}에 '{col}' 컬럼이 없음")

    df = df[df["record_type"].astype(str) == "time"].copy()

    if df.empty:
        raise ValueError("time 데이터가 없음")

    # 첫 번째 더미 샘플 제거
    if DROP_FIRST_DUMMY_SAMPLE:
        df = df[
            ~(
                (df["frame_index"] == 0) &
                (df["sample_or_bin_index"] == 0)
            )
        ].copy()

    run_id, device, mode = infer_meta_from_df(df, time_csv_path)

    rows = []

    for frame_idx, g in df.groupby("frame_index"):
        g = g.sort_values("sample_or_bin_index").copy()

        t = pd.to_numeric(g["timestamp"], errors="coerce").dropna().values

        ch0 = pd.to_numeric(g["ch0_adc_centered"], errors="coerce").dropna().values
        ch1 = pd.to_numeric(g["ch1_adc_centered"], errors="coerce").dropna().values

        n = min(len(ch0), len(ch1), len(t))

        if n < 10:
            continue

        ch0 = ch0[:n]
        ch1 = ch1[:n]
        t = t[:n]

        ch0_clean = clean_signal(ch0)
        ch1_clean = clean_signal(ch1)

        p_inst = ch0_clean * ch1_clean

        vrms_adc = rms(ch0_clean)
        irms_adc = rms(ch1_clean)

        vpeak_adc = float(np.max(np.abs(ch0_clean)))
        ipeak_adc = float(np.max(np.abs(ch1_clean)))

        vpp_adc = p2p(ch0_clean)
        ipp_adc = p2p(ch1_clean)

        iabs_mean_adc = float(np.mean(np.abs(ch1_clean)))
        istd_adc = float(np.std(ch1_clean))

        crest_factor_i = float(ipeak_adc / irms_adc) if irms_adc > EPS else 0.0

        p_proxy = float(np.mean(p_inst))
        pabs_mean_proxy = float(np.mean(np.abs(p_inst)))
        ppeak_proxy = float(np.max(np.abs(p_inst)))
        pstd_proxy = float(np.std(p_inst))

        # fs_actual 컬럼이 있으면 우선 사용
        if "fs_actual" in g.columns and g["fs_actual"].notna().any():
            fs_actual = safe_float(g["fs_actual"].dropna().iloc[0], 0.0)
        else:
            fs_actual = calc_fs_from_timestamps(t)

        rows.append({
            "run_id": run_id,
            "device": device,
            "mode": mode,
            "source_time_file": os.path.basename(time_csv_path),
            "frame_index": int(frame_idx),
            "time": float(t[0]),
            "n_samples": int(n),
            "fs_actual": round(fs_actual, 3),

            "Vrms_adc": round(vrms_adc, 6),
            "Irms_adc": round(irms_adc, 6),
            "Vpeak_adc": round(vpeak_adc, 6),
            "Ipeak_adc": round(ipeak_adc, 6),
            "Vpp_adc": round(vpp_adc, 6),
            "Ipp_adc": round(ipp_adc, 6),
            "Iabs_mean_adc": round(iabs_mean_adc, 6),
            "Istd_adc": round(istd_adc, 6),
            "crest_factor_i": round(crest_factor_i, 6),

            "P_proxy": round(p_proxy, 6),
            "Pabs_mean_proxy": round(pabs_mean_proxy, 6),
            "Ppeak_proxy": round(ppeak_proxy, 6),
            "Pstd_proxy": round(pstd_proxy, 6),
        })

    out = pd.DataFrame(rows)

    if out.empty:
        raise ValueError("time summary 생성 결과가 비어 있음")

    out = out.sort_values("frame_index").reset_index(drop=True)
    out["elapsed_s"] = out["time"] - out["time"].iloc[0]

    return out


# =========================================================
# 4. Baseline / delta / state 추가
# =========================================================

def add_state_features(summary_df):
    df = summary_df.copy()

    # baseline은 초기 프레임 기준
    baseline_part = df.head(BASELINE_FRAMES)

    baseline_irms = float(baseline_part["Irms_adc"].mean())
    baseline_p = float(baseline_part["P_proxy"].mean())

    noise_i = float(baseline_part["Irms_adc"].std(ddof=0))
    noise_p = float(baseline_part["P_proxy"].std(ddof=0))

    thr_i = max(noise_i * THRESHOLD_SIGMA_I, MIN_THRESHOLD_I)
    thr_p = max(noise_p * THRESHOLD_SIGMA_P, MIN_THRESHOLD_P)

    df["baseline_Irms_adc"] = baseline_irms
    df["baseline_P_proxy"] = baseline_p

    df["delta_Irms_adc"] = df["Irms_adc"] - baseline_irms
    df["delta_P_proxy"] = df["P_proxy"] - baseline_p

    df["delta_Irms_adc_avg"] = moving_average_series(df["delta_Irms_adc"], DELTA_SMOOTH_WINDOW)
    df["delta_P_proxy_avg"] = moving_average_series(df["delta_P_proxy"], DELTA_SMOOTH_WINDOW)

    states = []
    prev_state = "OFF"

    for _, row in df.iterrows():
        di = abs(float(row["delta_Irms_adc_avg"]))
        dp = abs(float(row["delta_P_proxy_avg"]))

        if prev_state == "OFF":
            if (di >= thr_i) or (dp >= thr_p):
                state = "ON"
            else:
                state = "OFF"
        else:
            if (di <= thr_i * OFF_RATIO) and (dp <= thr_p * OFF_RATIO):
                state = "OFF"
            else:
                state = "ON"

        states.append(state)
        prev_state = state

    df["state"] = states

    # auto_level: ON이면 mode, OFF면 OFF
    df["auto_level"] = np.where(df["state"] == "ON", df["mode"], "OFF")

    # state 변화점 기준 transient 표시
    state_changed = df["state"] != df["state"].shift(1)
    change_indices = df.index[state_changed].tolist()

    df["is_transient"] = False

    for idx in change_indices:
        start = max(0, idx - TRANSIENT_MARGIN_FRAMES)
        end = min(len(df) - 1, idx + TRANSIENT_MARGIN_FRAMES)
        df.loc[start:end, "is_transient"] = True

    # 첫 프레임은 baseline 시작점이므로 transient에서 제외
    if len(df) > 0:
        df.loc[0, "is_transient"] = False

    # 학습 유효 구간: ON이면서 과도 구간이 아닌 부분
    df["valid_for_training"] = (df["state"] == "ON") & (~df["is_transient"])

    # threshold 정보 저장
    df["thr_Irms_adc"] = round(thr_i, 6)
    df["thr_P_proxy"] = round(thr_p, 6)

    return df


# =========================================================
# 5. FFT RAW → fft summary
# =========================================================

def build_fft_summary(fft_csv_path):
    df = pd.read_csv(fft_csv_path)

    required_cols = [
        "run_id",
        "device",
        "mode",
        "record_type",
        "frame_index",
        "sample_or_bin_index",
        "timestamp",
        "frequency_hz",
        "fft_magnitude",
    ]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"{os.path.basename(fft_csv_path)}에 '{col}' 컬럼이 없음")

    df = df[df["record_type"].astype(str) == "fft"].copy()

    if df.empty:
        raise ValueError("fft 데이터가 없음")

    run_id, device, mode = infer_meta_from_df(df, fft_csv_path)

    rows = []

    for frame_idx, g in df.groupby("frame_index"):
        g = g.sort_values("sample_or_bin_index").copy()

        t = pd.to_numeric(g["timestamp"], errors="coerce").dropna().values
        if len(t) == 0:
            continue

        h_values = {}
        for name, freq in TARGET_FREQS.items():
            h_values[name] = get_nearest_fft_value(g, freq)

        h1 = h_values["H1_60_mag"]
        h3 = h_values["H3_180_mag"]
        h5 = h_values["H5_300_mag"]
        h7 = h_values["H7_420_mag"]

        if pd.isna(h1) or h1 <= EPS:
            thd_i = np.nan
            h3_ratio = np.nan
            h5_ratio = np.nan
            h7_ratio = np.nan
        else:
            thd_i = float(np.sqrt(h3 ** 2 + h5 ** 2 + h7 ** 2) / h1)
            h3_ratio = float(h3 / h1)
            h5_ratio = float(h5 / h1)
            h7_ratio = float(h7 / h1)

        # peak freq는 30Hz 제외하고 60Hz 이상에서 탐색
        g_valid_peak = g[pd.to_numeric(g["frequency_hz"], errors="coerce") >= 60].copy()

        if g_valid_peak.empty:
            peak_freq = np.nan
            peak_mag = np.nan
        else:
            mags = pd.to_numeric(g_valid_peak["fft_magnitude"], errors="coerce")
            idx_max = mags.idxmax()
            peak_freq = float(g_valid_peak.loc[idx_max, "frequency_hz"])
            peak_mag = float(g_valid_peak.loc[idx_max, "fft_magnitude"])

        rows.append({
            "fft_frame_index": int(frame_idx),
            "fft_time": float(t[0]),
            "source_fft_file": os.path.basename(fft_csv_path),

            "H1_60_mag": round(h1, 6) if not pd.isna(h1) else np.nan,
            "H3_180_mag": round(h3, 6) if not pd.isna(h3) else np.nan,
            "H5_300_mag": round(h5, 6) if not pd.isna(h5) else np.nan,
            "H7_420_mag": round(h7, 6) if not pd.isna(h7) else np.nan,

            "THD_i": round(thd_i, 6) if not pd.isna(thd_i) else np.nan,
            "H3_ratio": round(h3_ratio, 6) if not pd.isna(h3_ratio) else np.nan,
            "H5_ratio": round(h5_ratio, 6) if not pd.isna(h5_ratio) else np.nan,
            "H7_ratio": round(h7_ratio, 6) if not pd.isna(h7_ratio) else np.nan,

            "fft_peak_freq": round(peak_freq, 3) if not pd.isna(peak_freq) else np.nan,
            "fft_peak_mag": round(peak_mag, 6) if not pd.isna(peak_mag) else np.nan,
        })

    out = pd.DataFrame(rows)

    if out.empty:
        raise ValueError("fft summary 생성 결과가 비어 있음")

    out = out.sort_values("fft_frame_index").reset_index(drop=True)
    out["fft_elapsed_s"] = out["fft_time"] - out["fft_time"].iloc[0]

    return out


# =========================================================
# 6. Time summary + FFT summary 병합
# =========================================================

def merge_time_fft_summary(time_summary, fft_summary):
    """
    time raw와 fft raw는 별도 실행으로 수집될 수 있으므로
    절대 timestamp가 아니라 elapsed_s 기준으로 가장 가까운 FFT frame을 붙임.
    """
    if fft_summary is None or fft_summary.empty:
        return time_summary

    left = time_summary.sort_values("elapsed_s").copy()
    right = fft_summary.sort_values("fft_elapsed_s").copy()

    merged = pd.merge_asof(
        left,
        right,
        left_on="elapsed_s",
        right_on="fft_elapsed_s",
        direction="nearest"
    )

    return merged


# =========================================================
# 7. FFT 파일 매칭
# =========================================================

def find_matching_fft_file(time_df, fft_files):
    """
    device, mode가 같은 FFT 파일을 찾음.
    여러 개면 파일 수정 시간이 가장 가까운 것을 사용.
    """
    if not fft_files:
        return None

    _, device, mode = infer_meta_from_df(time_df, "")

    candidates = []

    for f in fft_files:
        try:
            df_head = pd.read_csv(f, nrows=5)
            _, d, m = infer_meta_from_df(df_head, f)

            if str(d).lower() == str(device).lower() and str(m).upper() == str(mode).upper():
                candidates.append(f)
        except Exception:
            continue

    if not candidates:
        return None

    return sorted(candidates, key=lambda x: os.path.getmtime(x))[-1]


# =========================================================
# 8. 메인 처리
# =========================================================

def process_one_time_file(time_file, fft_files):
    print(f"\n[PROCESS] time file: {os.path.basename(time_file)}")

    # time summary 생성
    time_summary = build_time_summary(time_file)
    time_summary = add_state_features(time_summary)

    # matching fft file 찾기
    time_df_head = pd.read_csv(time_file, nrows=5)
    fft_file = find_matching_fft_file(time_df_head, fft_files)

    if fft_file is not None:
        print(f"[MATCH] fft file : {os.path.basename(fft_file)}")
        fft_summary = build_fft_summary(fft_file)
        final_summary = merge_time_fft_summary(time_summary, fft_summary)
    else:
        print("[MATCH] fft file 없음 → time feature만 사용")
        final_summary = time_summary

    run_id = str(final_summary["run_id"].iloc[0])
    device = str(final_summary["device"].iloc[0])
    mode = str(final_summary["mode"].iloc[0])

    out_name = f"summary_{device}_{mode}_{run_id}.csv"
    out_path = os.path.join(SUMMARY_DIR, out_name)

    final_summary.to_csv(out_path, index=False)

    print(f"[SAVE] {out_path}")
    print(f"[INFO] rows={len(final_summary)}")
    print(f"[INFO] ON frames={(final_summary['state'] == 'ON').sum()}")
    print(f"[INFO] valid_for_training={final_summary['valid_for_training'].sum()}")

    return out_path


def main():
    time_files = sorted(glob.glob(TIME_PATTERN))
    fft_files = sorted(glob.glob(FFT_PATTERN))

    print("=== NILM RAW → SUMMARY 전처리 시작 ===")
    print("BASE_DIR:", BASE_DIR)
    print("time raw 개수:", len(time_files))
    print("fft raw 개수 :", len(fft_files))

    if not time_files:
        print("[INFO] time raw 파일이 없음")
        return

    out_files = []

    for time_file in time_files:
        try:
            out_path = process_one_time_file(time_file, fft_files)
            out_files.append(out_path)
        except Exception as e:
            print(f"[ERROR] {os.path.basename(time_file)} 처리 실패: {e}")

    print("\n=== 완료 ===")
    print("생성된 summary 파일:")
    for f in out_files:
        print("-", f)


if __name__ == "__main__":
    main()
    