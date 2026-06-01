#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4_visualize_raw_waveforms.py
============================
Data/RAW/ 의 가전별 시간영역 파형(오실로스코프) + 주파수 스펙트럼을 표시한다.
수집 데이터가 실제 오실로스코프 측정값과 일치하는지, 시연 화면과 동일한 형태를
가지는지 시각적으로 검증하기 위한 도구. 추론 파이프라인과 무관하므로 Mac 에서
바로 실행 가능.

두 개의 figure 를 띄운다.
  - figure 1: 일반 가전 4 개 (charger / tv / cleaner / microwave)
  - figure 2: dryer 6 모드 (SLOW_LOW / SLOW_MID / SLOW_HIGH / FAST_LOW / FAST_MID / FAST_HIGH)

각 행은 좌측에 시간영역(V=magenta 좌축, I=cyan 우축), 우측에 16-bin FFT.
표시 frame 은 자동으로 "가장 활성된 (ch1 std 가 큰) frame" 을 고른다 (idle 구간을
직선으로 그리지 않기 위해). `--frame N` 으로 강제 지정 가능.

사용 예:
    python RaspberryPi/NILM/4_visualize_raw_waveforms.py
    python RaspberryPi/NILM/4_visualize_raw_waveforms.py --target dryer
    python RaspberryPi/NILM/4_visualize_raw_waveforms.py --frame 150
"""

import os
import glob
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Data", "RAW"))

# 일반 가전 (단일 모드 — 표시 순서는 전류 크기 오름차순)
BASIC_DEVICES = ["charger", "tv", "cleaner", "microwave"]

# Dryer: (speed, power) 2-토큰 모드
DRYER_MODES = [
    ("SLOW", "LOW"),
    ("SLOW", "MID"),
    ("SLOW", "HIGH"),
    ("FAST", "LOW"),
    ("FAST", "MID"),
    ("FAST", "HIGH"),
]

TARGET_FFT_FREQS = [60, 180, 300, 420]


# =====================================================================
# 파일 / 데이터 로딩
# =====================================================================

def find_csv(device, record_type, mode_tokens=None):
    """
    Data/RAW/ 에서 raw_{device}_*_{record_type}_*.csv 파일 검색.
    mode_tokens=("SLOW","HIGH") 가 주어지면 파일명에 그 토큰 조합이 포함된 파일만.
    정렬 후 첫 파일 반환 (= 같은 모드의 첫 측정).
    """
    pattern = os.path.join(RAW_DIR, f"raw_{device}_*_{record_type}_*.csv")
    files = sorted(glob.glob(pattern))
    if mode_tokens:
        want = "_".join(mode_tokens).upper()
        files = [f for f in files if want in os.path.basename(f).upper()]
    return files[0] if files else None


def pick_active_time_frame(df):
    """ch1 std 가 가장 큰 frame_index 반환. frame=10 처럼 가전 OFF 인 idle 구간 회피."""
    stats = df.groupby("frame_index")["ch1_adc_centered"].std()
    if stats.empty or float(stats.max()) == 0.0:
        return int(df["frame_index"].iloc[0])
    return int(stats.idxmax())


def pick_active_fft_frame(df):
    """FFT magnitude 합이 가장 큰 frame_index 반환."""
    sums = df.groupby("frame_index")["fft_magnitude"].sum()
    if sums.empty or float(sums.max()) == 0.0:
        return int(df["frame_index"].iloc[0])
    return int(sums.idxmax())


def load_time_frame(csv_path, frame_idx=None):
    df = pd.read_csv(csv_path)
    available = set(df["frame_index"].unique())
    if frame_idx is None or frame_idx not in available:
        frame_idx = pick_active_time_frame(df)
    sub = df[df["frame_index"] == frame_idx]
    ch0 = sub["ch0_adc_centered"].to_numpy(dtype=float)
    ch1 = sub["ch1_adc_centered"].to_numpy(dtype=float)
    fs = 1920.0
    if "fs_actual" in sub.columns:
        v = sub["fs_actual"].dropna()
        if len(v):
            fs = float(v.iloc[0])
    return ch0, ch1, fs, int(frame_idx)


def load_fft_frame(csv_path, frame_idx=None):
    df = pd.read_csv(csv_path)
    available = set(df["frame_index"].unique())
    if frame_idx is None or frame_idx not in available:
        frame_idx = pick_active_fft_frame(df)
    sub = df[df["frame_index"] == frame_idx]
    freqs = sub["frequency_hz"].to_numpy(dtype=float)
    mags = sub["fft_magnitude"].to_numpy(dtype=float)
    return freqs, mags, int(frame_idx)


# =====================================================================
# 플로팅 헬퍼
# =====================================================================

def _style_axes(ax):
    ax.set_facecolor('black')
    ax.tick_params(colors='white', labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('gray')


def _sym_ylim(arr, floor=20.0, margin=1.25):
    """0 중심 대칭 ylim. floor 로 너무 작은 신호도 최소 시각 폭 보장."""
    if len(arr) == 0:
        return -floor, floor
    arr = np.asarray(arr, dtype=float)
    center = float(np.mean(arr))
    half = max(float(np.max(np.abs(arr - center))), floor) * margin
    return center - half, center + half


def plot_time(ax_left, ax_right, ch0, ch1, fs, frame, title):
    """ch0 (전압) 은 좌측 y축(magenta), ch1 (전류) 는 우측 y축(cyan).
    DC offset 이 있어도 각자 자기 범위로 auto-scale 되므로 둘 다 잘 보인다."""
    n = len(ch0)

    line_v, = ax_left.plot(ch0,  color='magenta', linewidth=1.4)
    line_i, = ax_right.plot(ch1, color='cyan',    linewidth=1.4)

    ax_left.set_ylim(*_sym_ylim(ch0))
    ax_right.set_ylim(*_sym_ylim(ch1))
    ax_left.set_xlim(0, n)

    ax_left.set_title(f"{title}  (fs={fs:.0f}Hz, frame={frame})",
                      color='white', fontsize=10)
    ax_left.set_ylabel("V (ADC)", color='magenta', fontsize=8)
    ax_right.set_ylabel("I (ADC)", color='cyan',    fontsize=8)

    ax_left.legend([line_v, line_i], ['V (CH0)', 'I (CH1)'],
                   loc='upper right', fontsize=8,
                   facecolor='black', labelcolor='white')
    ax_left.grid(True, linestyle='--', alpha=0.3)

    _style_axes(ax_left)
    _style_axes(ax_right)
    ax_left.tick_params(axis='y',  colors='magenta')
    ax_right.tick_params(axis='y', colors='cyan')


def plot_fft(ax, freqs, mags, frame, title):
    ax.bar(freqs, mags, color='lime', width=15)
    ax.set_xlim(0, 500)
    mx = float(np.max(mags)) if len(mags) else 0.0
    ax.set_ylim(0, max(mx * 1.2, 100.0))
    ax.set_title(f"{title}  spectrum  (frame={frame})",
                 color='white', fontsize=10)
    ax.set_xticks(TARGET_FFT_FREQS)
    ax.set_xticklabels([f"{f}Hz" for f in TARGET_FFT_FREQS],
                       color='yellow', fontweight='bold', fontsize=9)
    ax.grid(True, axis='x', color='yellow', linestyle=':', alpha=0.5)
    ax.grid(True, axis='y', linestyle='--', alpha=0.3)
    _style_axes(ax)


def _row_render(ax_t, ax_t_r, ax_f, label, device, record_args, frame_arg):
    """한 행 (time + fft) 렌더링.
    record_args: find_csv 에 넘길 추가 인자 (mode_tokens 등) — dict."""
    tfile = find_csv(device, "time", **record_args)
    if tfile:
        ch0, ch1, fs, fr = load_time_frame(tfile, frame_arg)
        plot_time(ax_t, ax_t_r, ch0, ch1, fs, fr, label)
    else:
        ax_t.set_title(f"{label} (no time CSV)", color='red')
        _style_axes(ax_t)

    ffile = find_csv(device, "fft", **record_args)
    if ffile:
        freqs, mags, fr = load_fft_frame(ffile, frame_arg)
        plot_fft(ax_f, freqs, mags, fr, label)
    else:
        ax_f.set_title(f"{label} (no fft CSV)", color='red')
        _style_axes(ax_f)


# =====================================================================
# Figure 렌더
# =====================================================================

def render_basic(frame_arg):
    fig, axes = plt.subplots(len(BASIC_DEVICES), 2, figsize=(14, 10))
    fig.canvas.manager.set_window_title("RAW Waveform Inspector - basic devices")
    fig.patch.set_facecolor('#1e1e1e')

    for row, dev in enumerate(BASIC_DEVICES):
        ax_t = axes[row, 0]
        ax_t_r = ax_t.twinx()
        ax_f = axes[row, 1]
        _row_render(ax_t, ax_t_r, ax_f, dev, dev, {}, frame_arg)

    fig.suptitle("Basic devices RAW  (active frame auto-selected per device)",
                 color='white', fontsize=12)
    plt.tight_layout(rect=(0, 0, 1, 0.97))


def render_dryer(frame_arg):
    fig, axes = plt.subplots(len(DRYER_MODES), 2, figsize=(14, 13))
    fig.canvas.manager.set_window_title("RAW Waveform Inspector - dryer 6 modes")
    fig.patch.set_facecolor('#1e1e1e')

    for row, mode_tokens in enumerate(DRYER_MODES):
        ax_t = axes[row, 0]
        ax_t_r = ax_t.twinx()
        ax_f = axes[row, 1]
        label = "dryer  " + "/".join(mode_tokens)
        _row_render(ax_t, ax_t_r, ax_f, label, "dryer",
                    {"mode_tokens": mode_tokens}, frame_arg)

    fig.suptitle("Dryer 6 modes RAW  (active frame auto-selected per mode)",
                 color='white', fontsize=12)
    plt.tight_layout(rect=(0, 0, 1, 0.97))


# =====================================================================
# CLI
# =====================================================================

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", type=int, default=None,
                        help="frame_index 강제 지정 (생략 시 ch1 std 가장 큰 active frame 자동 선택)")
    parser.add_argument("--target", choices=["all", "basic", "dryer"],
                        default="all",
                        help="어떤 figure 를 띄울지 (기본 all)")
    args = parser.parse_args()

    if args.target in ("all", "basic"):
        render_basic(args.frame)
    if args.target in ("all", "dryer"):
        render_dryer(args.frame)

    plt.show()


if __name__ == "__main__":
    main()
