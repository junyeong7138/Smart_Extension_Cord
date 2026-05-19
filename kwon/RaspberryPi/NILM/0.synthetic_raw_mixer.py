#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# 1. 기본 경로 / 설정
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Data", "RAW"))

BASELINE_FRAMES = 10
EPS = 1e-9

REQUIRED_COLS = [
    "record_type",
    "frame_index",
    "sample_or_bin_index",
    "timestamp",
    "ch0_adc_centered",
    "ch1_adc_centered",
]


# =========================================================
# 2. 유틸 함수
# =========================================================

def safe_num(s):
    return pd.to_numeric(s, errors="coerce")


def load_time_raw(path):
    df = pd.read_csv(path)

    for col in REQUIRED_COLS:
        if col not in df.columns:
            raise ValueError(f"{os.path.basename(path)}: '{col}' 컬럼 없음")

    df = df[df["record_type"].astype(str).str.lower() == "time"].copy()

    if df.empty:
        raise ValueError(f"{os.path.basename(path)}: record_type=time 데이터 없음")

    df["frame_index"] = safe_num(df["frame_index"]).astype(int)
    df["sample_or_bin_index"] = safe_num(df["sample_or_bin_index"]).astype(int)
    df["timestamp"] = safe_num(df["timestamp"])
    df["ch0_adc_centered"] = safe_num(df["ch0_adc_centered"])
    df["ch1_adc_centered"] = safe_num(df["ch1_adc_centered"])

    df = df.dropna(subset=[
        "frame_index",
        "sample_or_bin_index",
        "timestamp",
        "ch0_adc_centered",
        "ch1_adc_centered",
    ])

    df = df.sort_values(["frame_index", "sample_or_bin_index"]).reset_index(drop=True)

    return df


def infer_device_mode(df, file_path):
    device = None
    mode = None

    if "device" in df.columns and df["device"].notna().any():
        device = str(df["device"].dropna().iloc[0]).strip().lower()

    if "mode" in df.columns and df["mode"].notna().any():
        mode = str(df["mode"].dropna().iloc[0]).strip().upper()

    if device and mode:
        return device, mode

    base = os.path.basename(file_path)
    name = os.path.splitext(base)[0]
    parts = name.split("_")

    # raw_dryer_SLOW_MID_time_...
    if len(parts) >= 4 and parts[0].lower() == "raw":
        try:
            time_idx = parts.index("time")
        except ValueError:
            time_idx = -1

        if time_idx > 1:
            middle = parts[1:time_idx]
            device = middle[0].lower()
            mode = "_".join(middle[1:]).upper() if len(middle) > 1 else "ON"
            return device, mode

    return "unknown", "UNKNOWN"


def pivot_signal(df, col):
    mat = df.pivot_table(
        index="frame_index",
        columns="sample_or_bin_index",
        values=col,
        aggfunc="mean",
    )

    mat = mat.sort_index(axis=0).sort_index(axis=1)

    return mat


def get_common_matrices(df_a, df_b):
    v_a = pivot_signal(df_a, "ch0_adc_centered")
    i_a = pivot_signal(df_a, "ch1_adc_centered")

    v_b = pivot_signal(df_b, "ch0_adc_centered")
    i_b = pivot_signal(df_b, "ch1_adc_centered")

    common_samples = sorted(
        set(v_a.columns)
        & set(i_a.columns)
        & set(v_b.columns)
        & set(i_b.columns)
    )

    if not common_samples:
        raise ValueError("공통 sample_or_bin_index가 없음")

    v_a = v_a[common_samples]
    i_a = i_a[common_samples]

    v_b = v_b[common_samples]
    i_b = i_b[common_samples]

    # A 기준 frame을 사용
    frames_a = list(v_a.index)
    frames_b = set(v_b.index)

    return v_a, i_a, v_b, i_b, frames_a, frames_b, common_samples


def calc_baseline_profile(mat, baseline_frames=BASELINE_FRAMES):
    """
    초기 OFF 구간의 sample별 baseline profile을 계산.
    단순 scalar 평균이 아니라 sample index별 평균을 구함.
    """
    if len(mat) < baseline_frames:
        raise ValueError(f"baseline frame 부족: {len(mat)} < {baseline_frames}")

    base = mat.iloc[:baseline_frames]
    profile = base.mean(axis=0)

    return profile


def align_b_to_a_by_frame(mat_b, frames_a, shift_frames):
    """
    A의 frame f에 대해 B의 frame f - shift_frames를 매칭.
    shift_frames > 0 이면 B가 나중에 켜지는 상황을 만들 수 있음.
    없는 frame은 NaN.
    """
    aligned_rows = []

    for f in frames_a:
        src_f = f - shift_frames

        if src_f in mat_b.index:
            aligned_rows.append(mat_b.loc[src_f].values)
        else:
            aligned_rows.append(np.full(mat_b.shape[1], np.nan))

    aligned = pd.DataFrame(
        aligned_rows,
        index=frames_a,
        columns=mat_b.columns,
    )

    return aligned


def fill_missing_with_baseline(mat, baseline_profile):
    out = mat.copy()

    for col in out.columns:
        out[col] = out[col].fillna(float(baseline_profile[col]))

    return out


def estimate_fs(df):
    t = safe_num(df["timestamp"]).dropna().values

    if len(t) < 2:
        return 0.0

    dt = np.diff(t)
    dt = dt[dt > 0]

    if len(dt) == 0:
        return 0.0

    return float(1.0 / np.mean(dt))


def reconstruct_raw_from_matrix(
    df_template,
    v_synth,
    i_synth,
    out_device,
    out_mode,
    out_run_id,
    source_a,
    source_b,
):
    """
    A raw의 frame/sample/timestamp 구조를 그대로 사용하고,
    ch0/ch1만 synthetic 값으로 교체.
    """
    df_out = df_template.copy()

    frame_col = df_out["frame_index"].astype(int).values
    sample_col = df_out["sample_or_bin_index"].astype(int).values

    v_values = []
    i_values = []

    for f, s in zip(frame_col, sample_col):
        if f in v_synth.index and s in v_synth.columns:
            v_values.append(float(v_synth.loc[f, s]))
            i_values.append(float(i_synth.loc[f, s]))
        else:
            v_values.append(np.nan)
            i_values.append(np.nan)

    df_out["ch0_adc_centered"] = v_values
    df_out["ch1_adc_centered"] = i_values

    df_out = df_out.dropna(subset=["ch0_adc_centered", "ch1_adc_centered"]).copy()

    df_out["device"] = out_device
    df_out["mode"] = out_mode
    df_out["run_id"] = out_run_id
    df_out["source_a"] = os.path.basename(source_a)
    df_out["source_b"] = os.path.basename(source_b)
    df_out["synthetic_method"] = "baseline_removed_current_sum"

    fs = estimate_fs(df_out)
    df_out["fs_actual"] = fs

    return df_out


# =========================================================
# 3. 핵심 합성 함수
# =========================================================

def synthesize_two_raw(
    raw_a_path,
    raw_b_path,
    output_path=None,
    shift_frames=0,
    scale_a=1.0,
    scale_b=1.0,
    out_device=None,
    out_mode=None,
):
    df_a = load_time_raw(raw_a_path)
    df_b = load_time_raw(raw_b_path)

    dev_a, mode_a = infer_device_mode(df_a, raw_a_path)
    dev_b, mode_b = infer_device_mode(df_b, raw_b_path)

    if out_device is None:
        out_device = f"{dev_a}_{dev_b}"

    if out_mode is None:
        out_mode = f"{mode_a}_{mode_b}_SYNTH"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_run_id = f"synth_{timestamp}"

    v_a, i_a, v_b, i_b, frames_a, frames_b, common_samples = get_common_matrices(df_a, df_b)

    # -----------------------------------------------------
    # baseline profile 계산
    # -----------------------------------------------------
    i_base_a = calc_baseline_profile(i_a, BASELINE_FRAMES)
    i_base_b = calc_baseline_profile(i_b, BASELINE_FRAMES)

    # B를 A 기준 frame에 맞춤
    i_b_aligned = align_b_to_a_by_frame(i_b, frames_a, shift_frames)
    i_b_aligned = fill_missing_with_baseline(i_b_aligned, i_base_b)

    # A도 결측이 있으면 A baseline으로 보정
    i_a_filled = fill_missing_with_baseline(i_a, i_base_a)

    # -----------------------------------------------------
    # 핵심: baseline 제거 후 부하 전류만 합산
    # -----------------------------------------------------
    load_i_a = i_a_filled - i_base_a
    load_i_b = i_b_aligned - i_base_b

    i_synth = i_base_a + (load_i_a * scale_a) + (load_i_b * scale_b)

    # -----------------------------------------------------
    # 전압은 더하지 않는다.
    # 공통 전원 파형이므로 A의 전압을 그대로 사용.
    # -----------------------------------------------------
    v_synth = v_a.copy()

    # template은 A raw의 frame/sample/timestamp 사용
    df_template = df_a[
        df_a["frame_index"].isin(frames_a)
        & df_a["sample_or_bin_index"].isin(common_samples)
    ].copy()

    df_out = reconstruct_raw_from_matrix(
        df_template=df_template,
        v_synth=v_synth,
        i_synth=i_synth,
        out_device=out_device,
        out_mode=out_mode,
        out_run_id=out_run_id,
        source_a=raw_a_path,
        source_b=raw_b_path,
    )

    if output_path is None:
        safe_device = out_device.lower()
        safe_mode = out_mode.upper()
        output_name = f"raw_{safe_device}_{safe_mode}_time_{out_run_id}.csv"
        output_path = os.path.join(RAW_DIR, output_name)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    df_out.to_csv(output_path, index=False)

    print("=== Synthetic RAW 생성 완료 ===")
    print("A =", raw_a_path)
    print("B =", raw_b_path)
    print("OUT =", output_path)
    print("device =", out_device)
    print("mode =", out_mode)
    print("run_id =", out_run_id)
    print("shift_frames =", shift_frames)
    print("scale_a =", scale_a)
    print("scale_b =", scale_b)
    print("rows =", len(df_out))
    print("frames =", df_out["frame_index"].nunique())
    print("samples/frame =", df_out["sample_or_bin_index"].nunique())
    print("method = baseline_removed_current_sum")

    return output_path


# =========================================================
# 4. main
# =========================================================

def main():
    parser = argparse.ArgumentParser(
        description="두 단일기기 RAW(time)를 baseline 제거 후 합성하는 NILM synthetic raw mixer"
    )

    parser.add_argument(
        "raw_a",
        help="첫 번째 단일기기 raw time CSV 경로"
    )

    parser.add_argument(
        "raw_b",
        help="두 번째 단일기기 raw time CSV 경로"
    )

    parser.add_argument(
        "--out",
        default=None,
        help="출력 synthetic raw CSV 경로"
    )

    parser.add_argument(
        "--shift-frames",
        type=int,
        default=0,
        help="B raw를 몇 frame 늦게 시작할지. 예: 50이면 A보다 B가 50 frame 늦게 추가됨"
    )

    parser.add_argument(
        "--scale-a",
        type=float,
        default=1.0,
        help="A 부하 전류 성분 scale"
    )

    parser.add_argument(
        "--scale-b",
        type=float,
        default=1.0,
        help="B 부하 전류 성분 scale"
    )

    parser.add_argument(
        "--device",
        default=None,
        help="출력 device 이름. 기본값: deviceA_deviceB"
    )

    parser.add_argument(
        "--mode",
        default=None,
        help="출력 mode 이름. 기본값: modeA_modeB_SYNTH"
    )

    args = parser.parse_args()

    synthesize_two_raw(
        raw_a_path=args.raw_a,
        raw_b_path=args.raw_b,
        output_path=args.out,
        shift_frames=args.shift_frames,
        scale_a=args.scale_a,
        scale_b=args.scale_b,
        out_device=args.device,
        out_mode=args.mode,
    )


if __name__ == "__main__":
    main()