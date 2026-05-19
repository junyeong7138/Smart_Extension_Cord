#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
2_make_summary.py

역할:
1. RAW time csv를 window/block 단위 summary feature csv로 변환
2. 새 파일명 구조 raw_device_state_mode_time_... 지원
3. 이전 once 파일명 구조 raw_device_mode_time_... 지원
4. *_fft_*.csv는 직접 사용하지 않음
5. time raw에서 FFT feature를 다시 계산함
6. fryer는 기본 제외
"""

import os
import sys
import glob
import numpy as np
import pandas as pd


# =========================================================
# 1. 경로 설정
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

if len(sys.argv) >= 2:
    DATASET_NAME = sys.argv[1]
else:
    DATASET_NAME = "state7"

RAW_DIR = os.path.join(PROJECT_DIR, "TrainWork", DATASET_NAME, "RAW")
SUMMARY_DIR = os.path.join(PROJECT_DIR, "TrainWork", DATASET_NAME, "SUMMARY")

os.makedirs(SUMMARY_DIR, exist_ok=True)

print("[PATH CHECK]")
print("BASE_DIR    =", BASE_DIR)
print("PROJECT_DIR =", PROJECT_DIR)
print("DATASET     =", DATASET_NAME)
print("RAW_DIR     =", RAW_DIR)
print("SUMMARY_DIR =", SUMMARY_DIR)


# =========================================================
# 2. 설정
# =========================================================

BLOCK_SIZE = 512
BLOCK_STEP = 256

DROP_FIRST_DUMMY_SAMPLE = True

USE_PERCENTILE_CLIP = True
CLIP_LOW_PCT = 1
CLIP_HIGH_PCT = 99

EPS = 1e-9

VALID_DEVICES = ["charger", "cooker", "dryer", "fan", "empty"]

# once_old처럼 ON/OFF가 섞인 파일에서 ON window 찾기용
MIN_DELTA_PABS_FOR_ON = 2500.0
MIN_DELTA_I_FOR_ON = 3.0
MIN_DELTA_H1_FOR_ON = 350.0

TRANSIENT_SKIP_BLOCKS_AFTER_EDGE = 2


# =========================================================
# 3. 파일명 파싱
# =========================================================

def parse_raw_filename(path):
    """
    새 구조:
        raw_dryer_on_FAST_LOW_time_20260517_171000.csv
        raw_fan_off_OFF_time_...
        raw_empty_none_NONE_time_...

    이전 once 구조:
        raw_dryer_FAST_LOW_time_...
        raw_fan_LOW_time_...
        raw_cooker_COOKING_time_...

    반환:
        device, file_state, mode, source_file, filename_style

    filename_style:
        "new_state_mode" : raw_device_state_mode_time
        "old_device_mode": raw_device_mode_time
    """

    source_file = os.path.basename(path)
    stem = os.path.splitext(source_file)[0]
    parts = stem.split("_")

    if len(parts) < 3 or parts[0].lower() != "raw":
        return "unknown", "unknown", "unknown", source_file, "unknown"

    device = parts[1].lower()

    # time 또는 fft 앞까지만 의미 있는 토큰
    tokens = []
    for p in parts[2:]:
        if p.lower() in ["time", "fft"]:
            break
        tokens.append(p)

    if len(tokens) == 0:
        return device, "unknown", "unknown", source_file, "unknown"

    first = tokens[0].lower()

    # 새 구조: raw_device_state_mode_time
    if first in ["on", "off", "empty", "none", "pluggedoff", "plugged_off"]:
        file_state = first

        if file_state in ["off", "pluggedoff", "plugged_off"]:
            file_state = "plugged_off"
        elif file_state in ["empty", "none"]:
            file_state = "empty"
        elif file_state == "on":
            file_state = "on"

        mode_tokens = tokens[1:]
        mode = "_".join(mode_tokens).lower() if mode_tokens else "unknown"

        return device, file_state, mode, source_file, "new_state_mode"

    # 이전 구조: raw_device_mode_time
    file_state = "unknown"
    mode = "_".join(tokens).lower()

    # 예전 파일명에 off/empty가 들어간 예외도 처리
    text = f"{device}_{mode}_{source_file}".lower()

    if "empty" in text or device in ["empty", "none", "no_load"]:
        file_state = "empty"
    elif "_off" in text or "off_" in text or "plugged_off" in text:
        file_state = "plugged_off"
    else:
        file_state = "on_candidate"

    return device, file_state, mode, source_file, "old_device_mode"


def is_time_raw_file(path):
    name = os.path.basename(path).lower()
    return name.endswith(".csv") and "_time_" in name


def should_exclude_file(path):
    name = os.path.basename(path).lower()

    # FFT csv는 직접 학습에 넣지 않음.
    # time csv에서 FFT feature를 다시 계산함.
    if "_fft_" in name:
        return True

    # 현재 class가 charger/cooker/dryer/fan이면 fryer는 제외
    if "fryer" in name:
        return True

    return False


# =========================================================
# 4. CSV 로드
# =========================================================

def find_column(df, candidates):
    lower_map = {str(c).lower(): c for c in df.columns}

    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]

    return None


def load_time_csv(path):
    df = pd.read_csv(path)

    time_col = find_column(df, ["time", "timestamp", "t", "sec", "seconds"])
    ch0_col = find_column(df, ["ch0", "CH0", "v", "voltage", "adc0", "channel0"])
    ch1_col = find_column(df, ["ch1", "CH1", "i", "current", "adc1", "channel1"])

    if ch0_col is None or ch1_col is None:
        raise ValueError(f"ch0/ch1 컬럼을 찾을 수 없음. columns={list(df.columns)}")

    ch0 = pd.to_numeric(df[ch0_col], errors="coerce").to_numpy(dtype=np.float64)
    ch1 = pd.to_numeric(df[ch1_col], errors="coerce").to_numpy(dtype=np.float64)

    mask = np.isfinite(ch0) & np.isfinite(ch1)
    ch0 = ch0[mask]
    ch1 = ch1[mask]

    fs = 1000.0

    if time_col is not None:
        t_all = pd.to_numeric(df[time_col], errors="coerce").to_numpy(dtype=np.float64)
        t = t_all[mask]
        t = t[np.isfinite(t)]

        if len(t) >= 2:
            dt = np.diff(t)
            dt = dt[np.isfinite(dt)]
            dt = dt[dt > 0]

            if len(dt) > 0:
                fs = float(1.0 / np.median(dt))

    if DROP_FIRST_DUMMY_SAMPLE and len(ch0) > 1:
        ch0 = ch0[1:]
        ch1 = ch1[1:]

    return ch0, ch1, fs


# =========================================================
# 5. feature 계산
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

    # ADC offset 제거
    x = x - np.mean(x)

    return x


def compute_features(ch0_block, ch1_block, fs):
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


# =========================================================
# 6. valid_for_training 처리
# =========================================================

def mark_valid_for_training(summary_df, file_state, filename_style):
    """
    새 파일:
        raw_device_on_mode_time
        raw_device_off_OFF_time
        raw_empty_none_NONE_time

        → 파일 전체가 상태 고정이라고 가정

    이전 once 파일:
        raw_device_mode_time

        → 앞부분 baseline 기준으로 ON window만 True
    """

    df = summary_df.copy()

    if len(df) == 0:
        df["state"] = []
        df["valid_for_training"] = []
        df["is_transient"] = []
        return df

    # empty
    if file_state == "empty":
        df["state"] = "empty"
        df["valid_for_training"] = False
        df["is_transient"] = False
        return df

    # plugged_off
    if file_state == "plugged_off":
        df["state"] = "plugged_off"
        df["valid_for_training"] = False
        df["is_transient"] = False
        return df

    # 새 구조의 on 파일은 전체 ON 안정 구간으로 간주
    if filename_style == "new_state_mode" and file_state == "on":
        df["state"] = "on"
        df["valid_for_training"] = True
        df["is_transient"] = False
        return df

    # 이전 once 구조는 파일 안에 OFF/ON이 섞였을 가능성이 있으므로
    # 앞부분 baseline 대비 변화량으로 ON window 판정
    n_base = max(3, min(10, len(df) // 5))
    base = df.iloc[:n_base]

    p0 = float(base["Pabs_mean_proxy"].median())
    i0 = float(base["Irms_adc"].median())
    h10 = float(base["H1_60_mag"].median())

    dp = (df["Pabs_mean_proxy"] - p0).abs()
    di = (df["Irms_adc"] - i0).abs()
    dh1 = (df["H1_60_mag"] - h10).abs()

    on_like = (
        (dp >= MIN_DELTA_PABS_FOR_ON)
        | (di >= MIN_DELTA_I_FOR_ON)
        | ((dp >= MIN_DELTA_PABS_FOR_ON * 0.5) & (dh1 >= MIN_DELTA_H1_FOR_ON))
    )

    is_transient = np.zeros(len(df), dtype=bool)
    on_arr = on_like.to_numpy(dtype=bool)

    for idx in range(1, len(on_arr)):
        if on_arr[idx] != on_arr[idx - 1]:
            start = max(0, idx - TRANSIENT_SKIP_BLOCKS_AFTER_EDGE)
            end = min(len(is_transient), idx + TRANSIENT_SKIP_BLOCKS_AFTER_EDGE + 1)
            is_transient[start:end] = True

    df["state"] = np.where(on_like, "on", "plugged_off")
    df["is_transient"] = is_transient
    df["valid_for_training"] = on_like & (~is_transient)

    return df


# =========================================================
# 7. 파일 처리
# =========================================================

def summarize_one_file(path):
    device, file_state, mode, source_file, filename_style = parse_raw_filename(path)

    ch0, ch1, fs = load_time_csv(path)

    if len(ch0) < BLOCK_SIZE:
        print(f"[SKIP] too short: {source_file}")
        return None

    rows = []
    block_idx = 0

    for start in range(0, len(ch0) - BLOCK_SIZE + 1, BLOCK_STEP):
        end = start + BLOCK_SIZE

        feat = compute_features(ch0[start:end], ch1[start:end], fs)

        feat.update({
            "source_file": source_file,
            "dataset_name": DATASET_NAME,
            "device": device,
            "file_state": file_state,
            "mode": mode,
            "filename_style": filename_style,
            "block_idx": block_idx,
            "start_sample": start,
            "end_sample": end,
            "fs": fs,
        })

        rows.append(feat)
        block_idx += 1

    summary = pd.DataFrame(rows)
    summary = mark_valid_for_training(summary, file_state, filename_style)

    return summary


def main():
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")))

    time_files = [
        f for f in files
        if is_time_raw_file(f) and not should_exclude_file(f)
    ]

    print("\n=== RAW FILE SUMMARY ===")
    print("전체 csv:", len(files))
    print("사용 time csv:", len(time_files))
    print("제외 csv:", len(files) - len(time_files))

    if not time_files:
        print("[ERROR] 사용할 time csv가 없습니다.")
        return

    for fpath in time_files:
        try:
            summary = summarize_one_file(fpath)

            if summary is None or len(summary) == 0:
                continue

            out_name = os.path.basename(fpath).replace("raw_", "summary_")
            out_path = os.path.join(SUMMARY_DIR, out_name)

            summary.to_csv(out_path, index=False)

            print(
                f"[OK] {os.path.basename(fpath)} -> {out_name} | "
                f"rows={len(summary)}, "
                f"state_count={summary['state'].value_counts().to_dict()}, "
                f"valid={int(summary['valid_for_training'].sum())}"
            )

        except Exception as e:
            print(f"[ERROR] {os.path.basename(fpath)} 실패: {e}")


if __name__ == "__main__":
    main()