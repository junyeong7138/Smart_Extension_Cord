#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3_train_device_classifier.py  (v2)
==================================
SUMMARY CSV를 읽어 RandomForest 가전 분류 모델을 학습한다.

v1 대비 변경점
--------------
1) window aggregation을 feature_extractor.aggregate_window_features 로 일원화
   → 학습/추론 분포 불일치 방지
2) device_prototypes 산출 방식을 median → mean 으로 변경
   (소수 outlier window가 median을 학습 결정경계 밖으로 끌고 가던 문제 완화)
3) class별 P_proxy / Irms / H1_60 의 (p10, p50, p90) range 저장
   → 추론 코드에서 P 기반 1차 후보 필터링에 사용
4) confusion matrix 및 클래스별 metric 로깅 강화
5) feature_extractor.FRAME_FEATURE_NAMES / WINDOW_FEATURE_NAMES 사용
   → 컬럼 순서를 절대 어긋나지 않도록 강제

v2 (2026-05-22): NILM 표준 4대 전력 feature 도입
   - feature_extractor 가 Vrms_adc / S_proxy / Q_proxy / PF_proxy 4종 추가
   - class_ranges 에 PF/Q/S 의 p10/p50/p90 도 저장 → 추론 단 활용 가능
   - device_prototypes 에 PF/Q/S 평균값 추가
   - 학습 컬럼 자동 확장 (WINDOW_FEATURE_NAMES 20 → 28)
   ⚠️ 재학습 전 SUMMARY 도 v2 feature_extractor 로 재생성 필요
      (기존 SUMMARY 의 raw Vrms_adc / 누락 컬럼이 학습에 섞이지 않도록)
"""

import sys
import os
import glob
import json
import joblib
import numpy as np
import pandas as pd

# 현재 파일이 있는 디렉토리의 상위 상위 경로를 시스템 패스에 추가
# RaspberryPi 폴더가 위치한 곳이 시스템 경로에 포함되어야 합니다.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    confusion_matrix,
)
from sklearn.ensemble import RandomForestClassifier

# 공용 feature 모듈 import (같은 폴더 또는 PYTHONPATH 안에 있어야 함)
from RaspberryPi.NILM.feature_extractor import (
    FRAME_FEATURE_NAMES,
    WINDOW_FEATURE_NAMES,
    aggregate_window_features,
    WINDOW_SIZE as FE_WINDOW_SIZE,
)

# =====================================================================
# 경로 설정 (기존과 동일)
# =====================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUMMARY_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Data", "SUMMARY"))
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Model"))
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "rf_device_classifier.joblib")
FEATURE_INFO_PATH = os.path.join(MODEL_DIR, "rf_device_features.json")

# =====================================================================
# 학습 설정
# =====================================================================
TARGET_TYPE = "device"
WINDOW_SIZE = FE_WINDOW_SIZE   # feature_extractor와 일치
WINDOW_STEP = 5                # 50% overlap

# 학습 대상 단일 가전 (summary CSV의 device 컬럼 기준)
VALID_SINGLE_DEVICES = ["charger", "microwave", "tv", "dryer", "cleaner"]

# Random Forest 하이퍼파라미터
RF_PARAMS = dict(
    n_estimators=300,
    max_depth=20,
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1,
)


# =====================================================================
# Summary CSV 로드 + window aggregation
# =====================================================================
def load_and_window_data():
    """
    SUMMARY 폴더의 모든 summary_*.csv를 읽어
    window 단위 학습 샘플을 생성.

    각 row는 feature_extractor.WINDOW_FEATURE_NAMES 컬럼을 가진다.
    """
    files = sorted(glob.glob(os.path.join(SUMMARY_DIR, "summary_*.csv")))
    all_windows = []

    for fpath in files:
        try:
            df = pd.read_csv(fpath)
            if len(df) == 0:
                continue

            device_name = str(df["device"].iloc[0]).lower()
            if device_name not in VALID_SINGLE_DEVICES:
                continue

            # 안정 ON 구간만 학습에 사용
            if "valid_for_training" in df.columns:
                df = df[df["valid_for_training"] == True].copy()

            if len(df) < WINDOW_SIZE:
                continue

            # window 생성
            for start in range(0, len(df) - WINDOW_SIZE + 1, WINDOW_STEP):
                win = df.iloc[start: start + WINDOW_SIZE]

                # FRAME_FEATURE_NAMES 컬럼이 summary에 있어야 함
                # → Step 3 전처리 코드가 동일 이름으로 컬럼을 만든다
                frame_dicts = []
                for _, row in win.iterrows():
                    fd = {}
                    for col in FRAME_FEATURE_NAMES:
                        if col in row and pd.notna(row[col]):
                            fd[col] = float(row[col])
                        else:
                            fd[col] = 0.0
                    frame_dicts.append(fd)

                # feature_extractor로 통일된 aggregation
                win_feat = aggregate_window_features(frame_dicts)
                win_feat["source_file"] = os.path.basename(fpath)
                win_feat["target"] = device_name
                all_windows.append(win_feat)

        except Exception as e:
            print(f"[ERROR] {os.path.basename(fpath)} 처리 실패: {e}")

    return pd.DataFrame(all_windows)


# =====================================================================
# 메인
# =====================================================================
def main():
    print("=" * 70)
    print("RF Device Classifier 학습 (v2)")
    print("=" * 70)
    print(f"SUMMARY_DIR : {SUMMARY_DIR}")
    print(f"MODEL_DIR   : {MODEL_DIR}")
    print(f"WINDOW_SIZE : {WINDOW_SIZE}")
    print(f"WINDOW_STEP : {WINDOW_STEP}")

    dataset = load_and_window_data()
    if len(dataset) == 0:
        print("❌ 학습 데이터가 없습니다. SUMMARY 폴더와 valid_for_training 확인 필요.")
        return

    # =================================================================
    # 데이터 분포 확인
    # =================================================================
    print("\n📊 클래스별 수집된 파일(Run) 개수:")
    print(dataset.groupby("target")["source_file"].nunique().to_string())
    print("\n📊 클래스별 window 개수:")
    print(dataset["target"].value_counts().to_string())
    print("-" * 70)

    # =================================================================
    # X / y / groups 분리 (컬럼 순서 강제)
    # =================================================================
    # feature_extractor.WINDOW_FEATURE_NAMES 순서로 정렬
    X = dataset[WINDOW_FEATURE_NAMES].fillna(0.0)
    y = dataset["target"]
    groups = dataset["source_file"]

    # =================================================================
    # Train/Test 분할 (같은 run의 window가 양쪽에 섞이지 않도록)
    # =================================================================
    n_classes = y.nunique()
    n_groups = groups.nunique()

    if n_groups < n_classes * 2:
        print(f"⚠️ Run 파일이 부족하여({n_groups} < {n_classes*2}) "
              f"Train/Test 분할 생략. 전체 데이터로 학습합니다.")
        X_train, X_test, y_train, y_test = X, X, y, y
        groups_train = groups
    else:
        gss = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
        train_idx, test_idx = next(gss.split(X, y, groups))
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        groups_train = groups.iloc[train_idx]

        print(f"\n📊 Train: {len(X_train)} window / Test: {len(X_test)} window")

    # =================================================================
    # 모델 학습
    # =================================================================
    print("\n🤖 RandomForest 학습 중...")
    model = RandomForestClassifier(**RF_PARAMS)
    model.fit(X_train, y_train)

    # =================================================================
    # 평가
    # =================================================================
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"\n✅ Accuracy : {acc:.4f}")
    print("\n[Classification Report]")
    print(classification_report(y_test, y_pred, zero_division=0))

    print("[Confusion Matrix] (row=true, col=pred)")
    cm = confusion_matrix(y_test, y_pred, labels=sorted(model.classes_))
    cm_df = pd.DataFrame(cm,
                         index=sorted(model.classes_),
                         columns=sorted(model.classes_))
    print(cm_df.to_string())

    print("\n[Feature Importance Top 10]")
    imp_pairs = sorted(
        zip(WINDOW_FEATURE_NAMES, model.feature_importances_),
        key=lambda x: -x[1]
    )
    for n, v in imp_pairs[:10]:
        print(f"  {n:30s} : {v:.4f}")

    # =================================================================
    # device_prototypes 생성 (median → mean 변경)
    # =================================================================
    # 추론 시 P 기반 보조 분류, REMOVE 시 매칭 등에 사용
    device_prototypes = {}
    class_ranges = {}    # 추가: 각 클래스의 P_proxy/Irms/H1 범위

    for dev in y_train.unique():
        sub = X_train[y_train == dev]
        if len(sub) == 0:
            continue

        device_prototypes[dev] = {
            "P_proxy":   float(sub["P_proxy_mean"].mean()),
            "Irms_adc":  float(sub["Irms_adc_mean"].mean()),
            "H1_60_mag": float(sub["H1_60_mag_mean"].mean()),
            # NILM 표준: PF/Q 는 기기별 위상특성을 잘 반영
            "PF_proxy":  float(sub["PF_proxy_mean"].mean()) if "PF_proxy_mean" in sub.columns else 0.0,
            "Q_proxy":   float(sub["Q_proxy_mean"].mean()) if "Q_proxy_mean" in sub.columns else 0.0,
            "S_proxy":   float(sub["S_proxy_mean"].mean()) if "S_proxy_mean" in sub.columns else 0.0,
        }

        # 추론 시 1차 후보 필터링용 range (p10, p50, p90)
        # 기존 P/Irms/H1 + NILM 표준 PF/Q/S 추가
        def _q(col, q):
            return float(sub[col].quantile(q)) if col in sub.columns else 0.0

        class_ranges[dev] = {
            "P_proxy_p10":  _q("P_proxy_mean", 0.10),
            "P_proxy_p50":  _q("P_proxy_mean", 0.50),
            "P_proxy_p90":  _q("P_proxy_mean", 0.90),
            "Irms_adc_p10":  _q("Irms_adc_mean", 0.10),
            "Irms_adc_p50":  _q("Irms_adc_mean", 0.50),
            "Irms_adc_p90":  _q("Irms_adc_mean", 0.90),
            "H1_60_mag_p10":  _q("H1_60_mag_mean", 0.10),
            "H1_60_mag_p50":  _q("H1_60_mag_mean", 0.50),
            "H1_60_mag_p90":  _q("H1_60_mag_mean", 0.90),
            # --- v2: NILM 표준 4대 전력 기반 range ---
            "PF_proxy_p10":  _q("PF_proxy_mean", 0.10),
            "PF_proxy_p50":  _q("PF_proxy_mean", 0.50),
            "PF_proxy_p90":  _q("PF_proxy_mean", 0.90),
            "Q_proxy_p10":   _q("Q_proxy_mean", 0.10),
            "Q_proxy_p50":   _q("Q_proxy_mean", 0.50),
            "Q_proxy_p90":   _q("Q_proxy_mean", 0.90),
            "S_proxy_p10":   _q("S_proxy_mean", 0.10),
            "S_proxy_p50":   _q("S_proxy_mean", 0.50),
            "S_proxy_p90":   _q("S_proxy_mean", 0.90),
        }

    print("\n[Device Prototypes (학습 mean)]")
    for dev, p in device_prototypes.items():
        print(f"  {dev:10s} P_proxy={p['P_proxy']:>12.2f}  "
              f"Irms={p['Irms_adc']:>8.3f}  H1_60={p['H1_60_mag']:>10.2f}")

    print("\n[Device P_proxy Range (p10 / p50 / p90)]")
    for dev, r in class_ranges.items():
        print(f"  {dev:10s} "
              f"{r['P_proxy_p10']:>10.1f} / "
              f"{r['P_proxy_p50']:>10.1f} / "
              f"{r['P_proxy_p90']:>10.1f}")

    print("\n[Device PF_proxy Range (p10 / p50 / p90)]  — 역률, 위상 특성")
    for dev, r in class_ranges.items():
        print(f"  {dev:10s} "
              f"{r['PF_proxy_p10']:>7.3f} / "
              f"{r['PF_proxy_p50']:>7.3f} / "
              f"{r['PF_proxy_p90']:>7.3f}")

    print("\n[Device Q_proxy Range (p10 / p50 / p90)]  — 무효전력")
    for dev, r in class_ranges.items():
        print(f"  {dev:10s} "
              f"{r['Q_proxy_p10']:>10.1f} / "
              f"{r['Q_proxy_p50']:>10.1f} / "
              f"{r['Q_proxy_p90']:>10.1f}")

    # =================================================================
    # Prototype 검증 (자기 자신을 잘 분류하는지)
    # =================================================================
    # v1에서 charger prototype을 모델에 넣었더니 fan으로 잘못 분류되던 문제 확인용
    print("\n[Prototype Self-Classification 검증]")
    for dev, p in device_prototypes.items():
        # prototype에 해당하는 가짜 window feature 생성 (mean만 채우고 std는 0)
        test_row = {fn: 0.0 for fn in WINDOW_FEATURE_NAMES}
        # 모든 mean feature는 그 클래스의 평균값으로
        sub = X_train[y_train == dev]
        for fn in WINDOW_FEATURE_NAMES:
            if fn in sub.columns:
                test_row[fn] = float(sub[fn].mean())

        df_test = pd.DataFrame([test_row])[WINDOW_FEATURE_NAMES]
        probs = model.predict_proba(df_test)[0]
        pred_class = model.classes_[np.argmax(probs)]
        prob_dict = {c: f"{p:.2f}" for c, p in zip(model.classes_, probs)}
        ok = "✓" if pred_class == dev else "✗"
        print(f"  {ok} {dev:10s} → pred={pred_class:10s}  probs={prob_dict}")

    # =================================================================
    # 저장
    # =================================================================
    joblib.dump(model, MODEL_PATH)

    info = {
        "target_type": TARGET_TYPE,
        "feature_names": WINDOW_FEATURE_NAMES,
        "window_size": WINDOW_SIZE,
        "window_step": WINDOW_STEP,
        "device_prototypes": device_prototypes,
        "class_ranges": class_ranges,
        "metrics": {
            "accuracy": float(acc),
            "n_train_window": int(len(X_train)),
            "n_test_window": int(len(X_test)),
            "classes": list(model.classes_),
        },
    }
    with open(FEATURE_INFO_PATH, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 저장 완료")
    print(f"   Model : {MODEL_PATH}")
    print(f"   Info  : {FEATURE_INFO_PATH}")


if __name__ == "__main__":
    main()
