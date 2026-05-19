#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
3_train_state_classifier.py

역할:
- state7 SUMMARY를 사용해서 상태 모델 학습
- 최종 출력 class:
    empty
    plugged_off
    on
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
    DATASET_NAME = sys.argv[1]
else:
    DATASET_NAME = "state7"

SUMMARY_DIR = os.path.join(PROJECT_DIR, "TrainWork", DATASET_NAME, "SUMMARY")
MODEL_DIR = os.path.join(PROJECT_DIR, "Model")

os.makedirs(MODEL_DIR, exist_ok=True)

STATE_MODEL_PATH = os.path.join(MODEL_DIR, "rf_state_classifier.joblib")
STATE_FEATURE_INFO_PATH = os.path.join(MODEL_DIR, "rf_state_features.json")
STATE_DEBUG_CSV = os.path.join(MODEL_DIR, "rf_state_training_dataset_debug.csv")
STATE_IMPORTANCE_CSV = os.path.join(MODEL_DIR, "rf_state_feature_importance.csv")


# =========================================================
# 2. 설정
# =========================================================

WINDOW_SIZE = 10
WINDOW_STEP = 5
RANDOM_STATE = 42

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

def safe_numeric(s):
    return pd.to_numeric(s, errors="coerce")


def normalize_state_label(x):
    x = str(x).strip().lower()

    if x in ["empty", "none", "no_load"]:
        return "empty"

    if x in ["plugged_off", "off", "standby", "idle"]:
        return "plugged_off"

    if x in ["on", "running"]:
        return "on"

    return None


def make_window_features(win, source_file, target_label):
    feat = {
        "source_file": source_file,
        "target_label": target_label,
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


def load_state_dataset():
    files = sorted(glob.glob(os.path.join(SUMMARY_DIR, "summary_*.csv")))
    rows = []

    print("[PATH CHECK]")
    print("SUMMARY_DIR =", SUMMARY_DIR)
    print("files       =", len(files))

    for fpath in files:
        try:
            df = pd.read_csv(fpath)

            if len(df) < WINDOW_SIZE:
                continue

            source_file = os.path.basename(fpath)

            if "state" not in df.columns:
                print(f"[SKIP] state 컬럼 없음: {source_file}")
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

                state_values = win["state"].astype(str).str.lower()
                mode_state = state_values.mode().iloc[0]
                target_label = normalize_state_label(mode_state)

                if target_label is None:
                    continue

                rows.append(make_window_features(win, source_file, target_label))
                used += 1

            print(f"[OK] {source_file} | windows={used}")

        except Exception as e:
            print(f"[ERROR] {os.path.basename(fpath)} 처리 실패: {e}")

    return pd.DataFrame(rows)


# =========================================================
# 4. main
# =========================================================

def main():
    print("\n=== STATE CLASSIFIER TRAIN START ===")

    dataset = load_state_dataset()

    if len(dataset) == 0:
        print("[ERROR] 학습 데이터가 없습니다.")
        return

    dataset.to_csv(STATE_DEBUG_CSV, index=False)

    print("\n=== Dataset Summary ===")
    print("총 window sample 수:", len(dataset))
    print("\n[State Counts]")
    print(dataset["target_label"].value_counts())
    print("\n[State별 source_file 개수]")
    print(dataset.groupby("target_label")["source_file"].nunique())

    feature_names = [c for c in dataset.columns if c not in ["source_file", "target_label"]]

    X = dataset[feature_names].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = dataset["target_label"]
    groups = dataset["source_file"]

    if len(y.unique()) < 2:
        print("[ERROR] state class가 2개 미만:", y.unique())
        return

    # 파일 단위 분리. 같은 파일에서 나온 window가 train/test에 동시에 들어가지 않게 함.
    gss = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=RANDOM_STATE)
    train_idx, test_idx = next(gss.split(X, y, groups))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=24,
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

    importance.to_csv(STATE_IMPORTANCE_CSV, index=False)

    print("\n=== Top 30 Feature Importances ===")
    print(importance.head(30).to_string(index=False))

    feature_info = {
        "model_type": "state_classifier",
        "class_labels": labels,
        "feature_names": feature_names,
        "window_size": WINDOW_SIZE,
        "window_step": WINDOW_STEP,
        "training_dataset": DATASET_NAME,
        "training_policy": "state7 only; labels are empty / plugged_off / on",
    }

    joblib.dump(model, STATE_MODEL_PATH)

    with open(STATE_FEATURE_INFO_PATH, "w", encoding="utf-8") as f:
        json.dump(feature_info, f, ensure_ascii=False, indent=2)

    print("\n=== 저장 완료 ===")
    print("STATE_MODEL_PATH        =", STATE_MODEL_PATH)
    print("STATE_FEATURE_INFO_PATH =", STATE_FEATURE_INFO_PATH)
    print("STATE_DEBUG_CSV         =", STATE_DEBUG_CSV)
    print("STATE_IMPORTANCE_CSV    =", STATE_IMPORTANCE_CSV)


if __name__ == "__main__":
    main()