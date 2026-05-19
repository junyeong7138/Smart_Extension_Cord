#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import json
import math
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.ensemble import RandomForestClassifier

# =========================================================
# 1. 경로 설정
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SUMMARY_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Data", "SUMMARY"))

MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Model"))
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "rf_device_classifier.joblib")
FEATURE_INFO_PATH = os.path.join(MODEL_DIR, "rf_device_features.json")
DATASET_DEBUG_CSV = os.path.join(MODEL_DIR, "rf_training_dataset_debug.csv")

# =========================================================
# 2. 학습 설정
# =========================================================

# 추천:
# 먼저 "device" 로 시작
# 나중에 파일 수 충분해지면 "device_mode" 시도
TARGET_TYPE = "device"
# TARGET_TYPE = "device_mode"

USE_VALID_FOR_TRAINING_ONLY = True
MIN_VALID_ROWS = 10

USE_DEDUPLICATION = True
DEDUP_ROUND_DECIMALS = 3

TEST_SIZE = 0.3
RANDOM_STATE = 42

# window 설정
WINDOW_SIZE = 10      # 5~10 추천
WINDOW_STEP = 10      # 겹치지 않게 10, 조금 겹치게 하려면 5
MIN_ROWS_PER_WINDOW = 5

# 너무 적은 클래스 제거 여부
DROP_CLASSES_WITH_LT_N_SAMPLES = 2

# =========================================================
# 3. Summary 파일 탐색
# =========================================================

def find_summary_files():
    pattern = os.path.join(SUMMARY_DIR, "summary_*.csv")
    return sorted(glob.glob(pattern))

# =========================================================
# 4. 라벨 추출
# =========================================================

def infer_device_label(df, file_path):
    if "device" in df.columns:
        vals = df["device"].dropna().astype(str).unique()
        if len(vals) > 0:
            return vals[0].strip().lower()

    base = os.path.basename(file_path)
    name = os.path.splitext(base)[0]
    parts = name.split("_")

    if len(parts) >= 2 and parts[0].lower() == "summary":
        return parts[1].strip().lower()

    return "unknown"


def infer_mode_label(df, file_path):
    if "mode" in df.columns:
        vals = df["mode"].dropna().astype(str).unique()
        if len(vals) > 0:
            return vals[0].strip().upper()

    base = os.path.basename(file_path)
    name = os.path.splitext(base)[0]
    parts = name.split("_")

    # 예: summary_dryer_SLOW_LOW_20260504_185700
    if len(parts) >= 4 and parts[0].lower() == "summary":
        mode_parts = []

        for p in parts[2:]:
            if p.isdigit() and len(p) == 8:
                break
            mode_parts.append(p)

        if mode_parts:
            return "_".join(mode_parts).upper()

    return "UNKNOWN"


def make_target_label(device_label, mode_label):
    if TARGET_TYPE == "device":
        return device_label

    if TARGET_TYPE == "mode":
        return mode_label

    if TARGET_TYPE == "device_mode":
        return f"{device_label}_{mode_label}".lower()

    raise ValueError(f"지원하지 않는 TARGET_TYPE: {TARGET_TYPE}")

# =========================================================
# 5. feature 후보
# =========================================================

NUMERIC_COLS_CANDIDATES = [
    # Time-domain feature
    "Vrms_adc",
    "Irms_adc",
    "Vpeak_adc",
    "Ipeak_adc",
    "Vpp_adc",
    "Ipp_adc",
    "Iabs_mean_adc",
    "Istd_adc",
    "crest_factor_i",

    # Power proxy feature
    "P_proxy",
    "Pabs_mean_proxy",
    "Ppeak_proxy",
    "Pstd_proxy",

    # Baseline / delta feature
    "baseline_Irms_adc",
    "baseline_P_proxy",
    "delta_Irms_adc",
    "delta_Irms_adc_avg",
    "delta_P_proxy",
    "delta_P_proxy_avg",
    "thr_Irms_adc",
    "thr_P_proxy",

    # Sampling
    "fs_actual",
    "n_samples",

    # FFT / harmonic feature
    "H1_60_mag",
    "H3_180_mag",
    "H5_300_mag",
    "H7_420_mag",
    "THD_i",
    "H3_ratio",
    "H5_ratio",
    "H7_ratio",
    "fft_peak_freq",
    "fft_peak_mag",
]

REQUIRED_BASIC = ["time", "Irms_adc", "P_proxy"]

# =========================================================
# 6. 공통 유틸
# =========================================================

def safe_stats(series, prefix):
    s = pd.to_numeric(series, errors="coerce")
    s = s.replace([np.inf, -np.inf], np.nan).dropna()

    if len(s) == 0:
        return {
            f"{prefix}_mean": 0.0,
            f"{prefix}_std": 0.0,
            f"{prefix}_min": 0.0,
            f"{prefix}_max": 0.0,
            f"{prefix}_median": 0.0,
        }

    return {
        f"{prefix}_mean": float(s.mean()),
        f"{prefix}_std": float(s.std(ddof=0)) if len(s) > 1 else 0.0,
        f"{prefix}_min": float(s.min()),
        f"{prefix}_max": float(s.max()),
        f"{prefix}_median": float(s.median()),
    }


def select_training_rows(df):
    """
    valid_for_training=True인 안정 ON 구간을 우선 사용.
    너무 적으면 전체 summary 사용.
    """
    if USE_VALID_FOR_TRAINING_ONLY and "valid_for_training" in df.columns:
        valid_mask = df["valid_for_training"].astype(str).str.lower().isin(
            ["true", "1", "yes"]
        )
        df_valid = df[valid_mask].copy()

        if len(df_valid) >= MIN_VALID_ROWS:
            return df_valid.reset_index(drop=True), "valid_for_training"

    return df.copy().reset_index(drop=True), "all_rows"


def extract_features_from_window(df_win):
    feat = {}

    for col in NUMERIC_COLS_CANDIDATES:
        if col in df_win.columns:
            feat.update(safe_stats(df_win[col], col))
        else:
            feat.update({
                f"{col}_mean": 0.0,
                f"{col}_std": 0.0,
                f"{col}_min": 0.0,
                f"{col}_max": 0.0,
                f"{col}_median": 0.0,
            })

    # 상태 비율
    if "state" in df_win.columns:
        state_str = df_win["state"].astype(str).str.upper()
        feat["on_ratio"] = float((state_str == "ON").mean())
        feat["off_ratio"] = float((state_str == "OFF").mean())
    else:
        feat["on_ratio"] = 0.0
        feat["off_ratio"] = 0.0

    # 과도 구간 비율
    if "is_transient" in df_win.columns:
        trans = df_win["is_transient"].astype(str).str.lower().isin(["true", "1", "yes"])
        feat["transient_ratio"] = float(trans.mean())
    else:
        feat["transient_ratio"] = 0.0

    # auto_level 종류 수
    if "auto_level" in df_win.columns:
        levels = df_win["auto_level"].dropna().astype(str)
        feat["auto_level_nunique"] = float(levels.nunique())
    else:
        feat["auto_level_nunique"] = 0.0

    feat["num_rows"] = float(len(df_win))
    return feat


def make_windows(df, window_size=10, step=10, min_rows=5):
    windows = []

    n = len(df)
    if n < min_rows:
        return windows

    for start in range(0, n, step):
        end = start + window_size
        win_df = df.iloc[start:end].copy()

        if len(win_df) < min_rows:
            continue

        windows.append((start, end, win_df))

    return windows

# =========================================================
# 7. 데이터셋 구성
# =========================================================

def build_dataset(summary_files):
    rows = []
    skipped = []

    for file_path in summary_files:
        try:
            df = pd.read_csv(file_path)

            if df.empty:
                raise ValueError("빈 summary 파일")

            for col in REQUIRED_BASIC:
                if col not in df.columns:
                    raise ValueError(f"'{col}' 컬럼 없음")

            device_label = infer_device_label(df, file_path)
            mode_label = infer_mode_label(df, file_path)

            if device_label == "unknown":
                raise ValueError("device 라벨 추출 실패")

            target_label = make_target_label(device_label, mode_label)

            df_train, row_policy = select_training_rows(df)

            windows = make_windows(
                df_train,
                window_size=WINDOW_SIZE,
                step=WINDOW_STEP,
                min_rows=MIN_ROWS_PER_WINDOW,
            )

            if len(windows) == 0:
                raise ValueError("window 생성 실패: valid row 부족")

            n_created = 0

            for window_idx, (start, end, win_df) in enumerate(windows):
                features = extract_features_from_window(win_df)

                features["target_label"] = target_label
                features["device_label"] = device_label
                features["mode_label"] = mode_label
                features["source_file"] = os.path.basename(file_path)
                features["row_policy"] = row_policy
                features["window_index"] = int(window_idx)
                features["row_start"] = int(start)
                features["row_end"] = int(min(end, len(df_train)))
                features["group_id"] = os.path.basename(file_path)   # 그룹 분할용

                rows.append(features)
                n_created += 1

            print(
                f"[OK] {os.path.basename(file_path)} "
                f"-> target={target_label} | valid_rows={len(df_train)} "
                f"| windows={n_created} | policy={row_policy}"
            )

        except Exception as e:
            skipped.append((file_path, str(e)))
            print(f"[SKIP] {os.path.basename(file_path)} | {e}")

    if not rows:
        raise RuntimeError("학습 가능한 summary 파일이 없음")

    dataset = pd.DataFrame(rows)
    return dataset, skipped

# =========================================================
# 8. 중복 제거
# =========================================================

def deduplicate_dataset(dataset):
    if not USE_DEDUPLICATION:
        return dataset

    ignore_cols = [
        "target_label",
        "device_label",
        "mode_label",
        "source_file",
        "row_policy",
        "window_index",
        "row_start",
        "row_end",
        "group_id",
    ]

    feature_cols = [c for c in dataset.columns if c not in ignore_cols]

    before = len(dataset)

    rounded = dataset[feature_cols].round(DEDUP_ROUND_DECIMALS)
    rounded["target_label"] = dataset["target_label"].values
    rounded["group_id"] = dataset["group_id"].values

    dup_mask = rounded.duplicated()
    dataset = dataset.loc[~dup_mask].reset_index(drop=True)

    after = len(dataset)

    print("\n=== Deduplication ===")
    print(f"Before : {before}")
    print(f"After  : {after}")
    print(f"Removed: {before - after}")

    return dataset


def drop_small_classes(dataset, min_samples=2):
    if min_samples <= 1:
        return dataset

    counts = dataset["target_label"].value_counts()
    keep_labels = counts[counts >= min_samples].index.tolist()

    dropped = counts[counts < min_samples]

    if len(dropped) > 0:
        print("\n=== Dropped Small Classes ===")
        print(dropped.to_string())

    filtered = dataset[dataset["target_label"].isin(keep_labels)].reset_index(drop=True)
    return filtered

# =========================================================
# 9. 학습
# =========================================================

def main():
    summary_files = find_summary_files()

    print("=== Random Forest 학습 시작 ===")
    print("BASE_DIR    =", BASE_DIR)
    print("SUMMARY_DIR =", SUMMARY_DIR)
    print("MODEL_DIR   =", MODEL_DIR)
    print("TARGET_TYPE =", TARGET_TYPE)
    print("summary 개수 =", len(summary_files))
    print("WINDOW_SIZE =", WINDOW_SIZE)
    print("WINDOW_STEP =", WINDOW_STEP)

    if not summary_files:
        print("[INFO] summary 파일이 없음")
        return

    dataset, skipped = build_dataset(summary_files)
    dataset = deduplicate_dataset(dataset)
    dataset = drop_small_classes(dataset, DROP_CLASSES_WITH_LT_N_SAMPLES)

    print("\n=== Dataset Preview ===")
    preview_cols = [
        "source_file", "device_label", "mode_label",
        "target_label", "row_policy", "window_index",
        "row_start", "row_end"
    ]
    print(dataset[preview_cols].head(20).to_string(index=False))

    print("\n=== Class Counts ===")
    print(dataset["target_label"].value_counts().to_string())

    print("\n=== File Counts per Class ===")
    file_counts = dataset.groupby("target_label")["source_file"].nunique().sort_values(ascending=False)
    print(file_counts.to_string())

    if dataset["target_label"].nunique() < 2:
        print("\n[INFO] target class가 1개뿐이라 분류 학습 불가")
        print("파일을 더 수집하거나 TARGET_TYPE을 더 단순하게 바꿔야 함")
        return

    if len(dataset) < 10:
        print("\n[INFO] window 샘플 수가 너무 적어 학습이 어려움")
        return

    # group 기준 분리
    groups = dataset["group_id"]
    y = dataset["target_label"]

    drop_cols = [
        "target_label",
        "device_label",
        "mode_label",
        "source_file",
        "row_policy",
        "window_index",
        "row_start",
        "row_end",
        "group_id",
    ]

    X = dataset.drop(columns=drop_cols)
    X = X.apply(pd.to_numeric, errors="coerce")
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    feature_names = list(X.columns)

    unique_groups = dataset["group_id"].nunique()
    if unique_groups < 2:
        print("\n[INFO] source_file 그룹이 1개뿐이라 그룹 분할 불가")
        return

    gss = GroupShuffleSplit(
        n_splits=1,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE
    )

    train_idx, test_idx = next(gss.split(X, y, groups=groups))

    X_train = X.iloc[train_idx].copy()
    X_test = X.iloc[test_idx].copy()
    y_train = y.iloc[train_idx].copy()
    y_test = y.iloc[test_idx].copy()

    train_groups = groups.iloc[train_idx].nunique()
    test_groups = groups.iloc[test_idx].nunique()

    print("\n=== Group Split Info ===")
    print(f"train samples = {len(X_train)}")
    print(f"test samples  = {len(X_test)}")
    print(f"train files   = {train_groups}")
    print(f"test files    = {test_groups}")

    print("\n=== Train Class Counts ===")
    print(y_train.value_counts().to_string())

    print("\n=== Test Class Counts ===")
    print(y_test.value_counts().to_string())

    # test에만 있고 train에 없는 클래스가 있으면 정확도 해석이 불가능해짐
    unseen_in_train = sorted(set(y_test.unique()) - set(y_train.unique()))
    if unseen_in_train:
        print("\n[WARN] test에만 있고 train에는 없는 클래스가 있음")
        print("       아래 클래스는 이번 split에서 절대 맞출 수 없음:")
        print("       ", unseen_in_train)
        print("       파일을 더 수집하거나 TARGET_TYPE을 단순화해야 함")

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("\n=== Accuracy ===")
    print(f"{accuracy_score(y_test, y_pred):.4f}")

    print("\n=== Classification Report ===")
    labels_report = sorted(set(y_train.unique()) | set(y_test.unique()))
    print(classification_report(y_test, y_pred, labels=labels_report, zero_division=0))

    print("\n=== Confusion Matrix ===")
    cm = confusion_matrix(y_test, y_pred, labels=labels_report)
    cm_df = pd.DataFrame(
        cm,
        index=[f"true_{x}" for x in labels_report],
        columns=[f"pred_{x}" for x in labels_report],
    )
    print(cm_df.to_string())

    importances = pd.Series(
        model.feature_importances_,
        index=feature_names
    ).sort_values(ascending=False)

    print("\n=== Top 20 Feature Importances ===")
    print(importances.head(20).round(6).to_string())

    # 저장
    joblib.dump(model, MODEL_PATH)

    feature_info = {
        "target_type": TARGET_TYPE,
        "feature_names": feature_names,
        "class_labels_train": sorted(y_train.unique().tolist()),
        "class_labels_test": sorted(y_test.unique().tolist()),
        "num_total_samples": int(len(X)),
        "num_train_samples": int(len(X_train)),
        "num_test_samples": int(len(X_test)),
        "num_total_files": int(dataset["source_file"].nunique()),
        "num_train_files": int(train_groups),
        "num_test_files": int(test_groups),
        "window_size": WINDOW_SIZE,
        "window_step": WINDOW_STEP,
        "summary_dir": SUMMARY_DIR,
    }

    with open(FEATURE_INFO_PATH, "w", encoding="utf-8") as f:
        json.dump(feature_info, f, ensure_ascii=False, indent=2)

    dataset.to_csv(DATASET_DEBUG_CSV, index=False)

    print("\n=== 저장 완료 ===")
    print("MODEL_PATH        =", MODEL_PATH)
    print("FEATURE_INFO_PATH =", FEATURE_INFO_PATH)
    print("DATASET_DEBUG_CSV =", DATASET_DEBUG_CSV)

    if skipped:
        print("\n=== Skipped Files ===")
        for path, reason in skipped:
            print(f"- {os.path.basename(path)} | {reason}")


if __name__ == "__main__":
    main()