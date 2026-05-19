#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
4_train_device_classifier.py

역할:
- ON 상태일 때 device 분류 모델 학습
- 최종 class:
    charger, cooker, dryer, fan

사용 데이터:
1. state7:
    새로 수집한 raw_device_state_mode_time 구조
    단, state == on인 window만 사용

2. device_on:
    새로 수집한 ON 전용 파일
    state == on인 window만 사용

3. once_old:
    이전 raw_device_mode_time 구조
    summary에서 valid_for_training == True인 ON window만 사용

제외:
- empty
- off / plugged_off
- fryer
- fft csv는 summary 단계에서 이미 제외
"""

import os
import sys
import glob
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# =========================================================
# 1. 경로 설정
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

if len(sys.argv) >= 2:
    DATASET_NAMES = sys.argv[1:]
else:
    DATASET_NAMES = ["state7", "device_on", "once_old"]

MODEL_DIR = os.path.join(PROJECT_DIR, "Model")
os.makedirs(MODEL_DIR, exist_ok=True)

DEVICE_MODEL_PATH = os.path.join(MODEL_DIR, "rf_device_classifier.joblib")
DEVICE_FEATURE_INFO_PATH = os.path.join(MODEL_DIR, "rf_device_features.json")
DEVICE_DEBUG_CSV = os.path.join(MODEL_DIR, "rf_device_training_dataset_debug.csv")
DEVICE_IMPORTANCE_CSV = os.path.join(MODEL_DIR, "rf_device_feature_importance.csv")


# =========================================================
# 2. 설정
# =========================================================

WINDOW_SIZE = 10
WINDOW_STEP = 5
RANDOM_STATE = 42

VALID_DEVICES = ["charger", "cooker", "dryer", "fan"]

# 필요하면 애매한 mode를 제외할 수 있음.
# 처음에는 False 추천.
EXCLUDE_COOKER_HEATING = False
EXCLUDE_FAN_MID = False

FEATURE_COLS = [
    "Vrms_adc", "Irms_adc", "Vpeak_adc", "Ipeak_adc", "Vpp_adc", "Ipp_adc",
    "Iabs_mean_adc", "Istd_adc", "crest_factor_i",
    "P_proxy", "Pabs_mean_proxy", "Ppeak_proxy", "Pstd_proxy",
    "H1_60_mag", "H3_180_mag", "H5_300_mag", "H7_420_mag",
    "THD_i", "H3_ratio", "H5_ratio", "H7_ratio",
    "fft_peak_freq", "fft_peak_mag",
]


# =========================================================
# 3. 함수
# =========================================================

def normalize_text(x):
    return str(x).strip().lower()


def safe_numeric(s):
    return pd.to_numeric(s, errors="coerce")


def normalize_device_name(device, source_file):
    d = normalize_text(device)
    f = normalize_text(source_file)

    if d in VALID_DEVICES:
        return d

    for dev in VALID_DEVICES:
        if dev in f:
            return dev

    return None


def should_skip_mode(device, mode, source_file):
    d = normalize_text(device)
    m = normalize_text(mode)
    f = normalize_text(source_file)
    text = f"{d}_{m}_{f}"

    if "fryer" in text:
        return True

    if "empty" in text:
        return True

    if EXCLUDE_COOKER_HEATING and d == "cooker" and "heating" in text:
        return True

    if EXCLUDE_FAN_MID and d == "fan" and "_mid" in text:
        return True

    return False


def is_true_like_series(s):
    if s.dtype == bool:
        return s

    return s.astype(str).str.lower().isin(["true", "1", "yes", "y"])


def is_on_window(win):
    """
    device 모델에는 ON window만 넣는다.
    우선순위:
    1. valid_for_training 평균이 0.6 이상이면 사용
    2. state가 on인 비율이 0.6 이상이면 사용
    """

    if "valid_for_training" in win.columns:
        valid = is_true_like_series(win["valid_for_training"])
        if valid.mean() >= 0.6:
            return True

    if "state" in win.columns:
        state = win["state"].astype(str).str.lower()
        if (state == "on").mean() >= 0.6:
            return True

    return False


def make_window_features(win, source_file, target_label, dataset_name, mode):
    feat = {
        "source_file": f"{dataset_name}/{source_file}",
        "target_label": target_label,
        "mode": mode,
    }

    for col in FEATURE_COLS:
        if col not in win.columns:
            continue

        s = safe_numeric(win[col]).replace([np.inf, -np.inf], np.nan).dropna()

        feat[f"{col}_mean"] = float(s.mean()) if len(s) else 0.0
        feat[f"{col}_std"] = float(s.std(ddof=0)) if len(s) else 0.0
        feat[f"{col}_min"] = float(s.min()) if len(s) else 0.0
        feat[f"{col}_max"] = float(s.max()) if len(s) else 0.0

    return feat


def load_dataset_from_summary(dataset_name):
    summary_dir = os.path.join(PROJECT_DIR, "TrainWork", dataset_name, "SUMMARY")
    files = sorted(glob.glob(os.path.join(summary_dir, "summary_*.csv")))

    print(f"\n[LOAD DATASET] {dataset_name}")
    print("SUMMARY_DIR =", summary_dir)
    print("files       =", len(files))

    rows = []

    for fpath in files:
        try:
            source_file = os.path.basename(fpath).lower()

            if "fryer" in source_file:
                print(f"[SKIP fryer] {source_file}")
                continue

            df = pd.read_csv(fpath)

            if len(df) < WINDOW_SIZE:
                continue

            device = str(df["device"].dropna().iloc[0]) if "device" in df.columns and df["device"].notna().any() else "unknown"
            mode = str(df["mode"].dropna().iloc[0]) if "mode" in df.columns and df["mode"].notna().any() else "unknown"

            target_device = normalize_device_name(device, source_file)

            if target_device is None:
                print(f"[SKIP unknown device] {source_file} | device={device}, mode={mode}")
                continue

            if target_device not in VALID_DEVICES:
                print(f"[SKIP invalid device] {source_file} | target={target_device}")
                continue

            if should_skip_mode(target_device, mode, source_file):
                print(f"[SKIP mode] {source_file} | device={target_device}, mode={mode}")
                continue

            work = df.copy()

            # 과도구간 제거
            if "is_transient" in work.columns:
                work = work[work["is_transient"] != True].copy()

            if len(work) < WINDOW_SIZE:
                continue

            used = 0

            for start in range(0, len(work) - WINDOW_SIZE + 1, WINDOW_STEP):
                win = work.iloc[start:start + WINDOW_SIZE]

                if not is_on_window(win):
                    continue

                rows.append(
                    make_window_features(
                        win=win,
                        source_file=os.path.basename(fpath),
                        target_label=target_device,
                        dataset_name=dataset_name,
                        mode=mode,
                    )
                )

                used += 1

            print(f"[OK] {source_file} | target={target_device} | mode={mode} | windows={used}")

        except Exception as e:
            print(f"[ERROR] {os.path.basename(fpath)} 처리 실패: {e}")

    return rows


# =========================================================
# 4. main
# =========================================================

def main():
    print("\n=== DEVICE CLASSIFIER TRAIN START ===")
    print("DATASET_NAMES =", DATASET_NAMES)

    all_rows = []

    for ds in DATASET_NAMES:
        all_rows.extend(load_dataset_from_summary(ds))

    dataset = pd.DataFrame(all_rows)

    if len(dataset) == 0:
        print("[ERROR] 학습 데이터가 없습니다.")
        return

    dataset.to_csv(DEVICE_DEBUG_CSV, index=False)

    print("\n=== Dataset Summary ===")
    print("총 window sample 수:", len(dataset))
    print("\n[Device Counts]")
    print(dataset["target_label"].value_counts())
    print("\n[Device별 source_file 개수]")
    print(dataset.groupby("target_label")["source_file"].nunique())

    if "mode" in dataset.columns:
        print("\n[Device / Mode Counts]")
        print(dataset.groupby(["target_label", "mode"]).size().sort_values(ascending=False))

    feature_names = [c for c in dataset.columns if c not in ["source_file", "target_label", "mode"]]

    X = dataset[feature_names].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = dataset["target_label"]
    groups = dataset["source_file"]

    if len(y.unique()) < 2:
        print("[ERROR] device class가 2개 미만:", y.unique())
        return

    gss = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=RANDOM_STATE)
    train_idx, test_idx = next(gss.split(X, y, groups))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    model = RandomForestClassifier(
        n_estimators=600,
        max_depth=28,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    print("\n=== 학습 중 ===")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\n=== Accuracy ===")
    print(f"{accuracy_score(y_test, y_pred):.4f}")

    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred, zero_division=0))

    labels = sorted(y.unique().tolist())
    cm = confusion_matrix(y_test, y_pred, labels=labels)

    print("\n=== Confusion Matrix ===")
    print(pd.DataFrame(cm, index=[f"true_{x}" for x in labels], columns=[f"pred_{x}" for x in labels]))

    importance = pd.DataFrame({
        "feature": feature_names,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)

    importance.to_csv(DEVICE_IMPORTANCE_CSV, index=False)

    print("\n=== Top 30 Feature Importances ===")
    print(importance.head(30).to_string(index=False))

    # device별 prototype 저장
    train_df = X_train.copy()
    train_df["target_label"] = y_train.values

    device_prototypes = {}

    for dev in sorted(y.unique()):
        sub = train_df[train_df["target_label"] == dev]

        device_prototypes[dev] = {
            "P_proxy": float(sub["P_proxy_mean"].median()) if "P_proxy_mean" in sub.columns else 0.0,
            "Pabs_mean_proxy": float(sub["Pabs_mean_proxy_mean"].median()) if "Pabs_mean_proxy_mean" in sub.columns else 0.0,
            "Irms_adc": float(sub["Irms_adc_mean"].median()) if "Irms_adc_mean" in sub.columns else 0.0,
            "H1_60_mag": float(sub["H1_60_mag_mean"].median()) if "H1_60_mag_mean" in sub.columns else 0.0,
            "THD_i": float(sub["THD_i_mean"].median()) if "THD_i_mean" in sub.columns else 0.0,
        }

    print("\n=== Device Prototypes ===")

    for dev, proto in device_prototypes.items():
        print(
            f"{dev:8s} | "
            f"P={proto['P_proxy']:.1f}, "
            f"Pabs={proto['Pabs_mean_proxy']:.1f}, "
            f"I={proto['Irms_adc']:.2f}, "
            f"H1={proto['H1_60_mag']:.1f}, "
            f"THD={proto['THD_i']:.4f}"
        )

    feature_info = {
        "model_type": "device_classifier_on_only",
        "class_labels": labels,
        "feature_names": feature_names,
        "window_size": WINDOW_SIZE,
        "window_step": WINDOW_STEP,
        "device_prototypes": device_prototypes,
        "training_policy": "ON windows only; new raw_device_state_mode + old raw_device_mode; fft features recomputed from time raw",
        "datasets": DATASET_NAMES,
        "excluded_policy": {
            "fryer": True,
            "fft_csv_direct_use": False,
            "off_empty_for_device": False,
            "EXCLUDE_COOKER_HEATING": EXCLUDE_COOKER_HEATING,
            "EXCLUDE_FAN_MID": EXCLUDE_FAN_MID,
        },
    }

    joblib.dump(model, DEVICE_MODEL_PATH)

    with open(DEVICE_FEATURE_INFO_PATH, "w", encoding="utf-8") as f:
        json.dump(feature_info, f, ensure_ascii=False, indent=2)

    print("\n=== 저장 완료 ===")
    print("DEVICE_MODEL_PATH        =", DEVICE_MODEL_PATH)
    print("DEVICE_FEATURE_INFO_PATH =", DEVICE_FEATURE_INFO_PATH)
    print("DEVICE_DEBUG_CSV         =", DEVICE_DEBUG_CSV)
    print("DEVICE_IMPORTANCE_CSV    =", DEVICE_IMPORTANCE_CSV)


if __name__ == "__main__":
    main()