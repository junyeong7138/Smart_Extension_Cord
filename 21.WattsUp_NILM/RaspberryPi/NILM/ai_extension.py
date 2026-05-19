#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import joblib
import numpy as np
import pandas as pd
from collections import deque

# 💡 기존 원본 파일들을 100% 그대로 재사용합니다!
from dsp_engine import DSPEngine
from dashboard_ui import DashboardUI

# AI 추론용 설정
WINDOW_SIZE = 10
BASELINE_FRAMES = 10
DELTA_SMOOTH_WINDOW = 3
THRESHOLD_SIGMA_I = 3.0
MIN_THRESHOLD_I = 20.0
OFF_RATIO = 0.6
EPS = 1e-9
CONFIDENCE_THRESHOLD = 0.50

NUMERIC_COLS_CANDIDATES = [
    "Vrms_adc", "Irms_adc", "Vpeak_adc", "Ipeak_adc", "Vpp_adc", "Ipp_adc",
    "Iabs_mean_adc", "Istd_adc", "crest_factor_i", "P_proxy", "Pabs_mean_proxy",
    "Ppeak_proxy", "Pstd_proxy", "baseline_Irms_adc", "baseline_P_proxy",
    "delta_Irms_adc", "delta_Irms_adc_avg", "delta_P_proxy", "delta_P_proxy_avg",
    "thr_Irms_adc", "thr_P_proxy", "fs_actual", "n_samples", "H1_60_mag",
    "H3_180_mag", "H5_300_mag", "H7_420_mag", "THD_i", "H3_ratio", "H5_ratio",
    "H7_ratio", "fft_peak_freq", "fft_peak_mag"
]

def clean_signal(x):
    x = np.asarray(x, dtype=np.float64)
    if len(x) == 0: return x
    lo, hi = np.percentile(x, 1), np.percentile(x, 99)
    return np.clip(x, lo, hi) if lo < hi else x

def safe_stats(series, prefix):
    s = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if len(s) == 0:
        return {f"{prefix}_mean": 0.0, f"{prefix}_std": 0.0, f"{prefix}_min": 0.0, f"{prefix}_max": 0.0, f"{prefix}_median": 0.0}
    return {
        f"{prefix}_mean": float(s.mean()), f"{prefix}_std": float(s.std(ddof=0)) if len(s)>1 else 0.0,
        f"{prefix}_min": float(s.min()), f"{prefix}_max": float(s.max()), f"{prefix}_median": float(s.median())
    }

# =========================================================
# 업그레이드 1: AI가 탑재된 엔진
# =========================================================
class AIEngine(DSPEngine):
    def __init__(self, spi_core, buffer_size=150):
        super().__init__(spi_core, buffer_size)
        
        self.ai_text = "🤖 AI: Model Setting..."
        
        # 모델 경로 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "Model"))
        self.model_path = os.path.join(model_dir, "rf_device_classifier.joblib")
        self.feature_info_path = os.path.join(model_dir, "rf_device_features.json")
        
        self.model = None
        self.expected_features = []
        
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                with open(self.feature_info_path, "r", encoding="utf-8") as f:
                    self.expected_features = json.load(f)["feature_names"]
                self.ai_text = "🤖 AI: Waiting (Device OFF)"
            except Exception as e:
                self.ai_text = "🤖 AI: Load Error"
        else:
            self.ai_text = "🤖 AI: No, Learning Model"

        # AI 연산용 상태 버퍼
        self.frame_count = 0
        self.baseline_rows = []
        self.baseline_irms, self.baseline_p = 0.0, 0.0
        self.thr_i, self.thr_p = MIN_THRESHOLD_I, 5000.0
        
        self.delta_i_history = deque(maxlen=DELTA_SMOOTH_WINDOW)
        self.delta_p_history = deque(maxlen=DELTA_SMOOTH_WINDOW)
        self.valid_on_buffer = deque(maxlen=WINDOW_SIZE)
        self.prob_history = deque(maxlen=3)
        self.current_state = "OFF"

    def process_raw_mode(self):
        # 💡 원본 기능(하드웨어 통신) 실행
        ch0, ch1, timestamps, fs_actual = super().process_raw_mode()
        
        # 💡 가져온 데이터로 백그라운드 AI 업데이트
        if self.model is not None and fs_actual > 0:
            self._run_ai_pipeline(ch0, ch1, fs_actual)
            
        return ch0, ch1, timestamps, fs_actual

    def _run_ai_pipeline(self, ch0, ch1, fs):
        try:
            # 1. Time & FFT Feature 추출
            ch0_c, ch1_c = clean_signal(ch0), clean_signal(ch1)
            irms = float(np.sqrt(np.mean(ch1_c**2)))
            vrms = float(np.sqrt(np.mean(ch0_c**2)))
            ipeak = float(np.max(np.abs(ch1_c)))
            p_inst = ch0_c * ch1_c
            p_proxy = float(np.mean(p_inst))
            
            feat = {
                "Vrms_adc": vrms, "Irms_adc": irms, 
                "Vpeak_adc": float(np.max(np.abs(ch0_c))), "Ipeak_adc": ipeak,
                "Vpp_adc": float(np.max(ch0_c) - np.min(ch0_c)), "Ipp_adc": float(np.max(ch1_c) - np.min(ch1_c)),
                "Iabs_mean_adc": float(np.mean(np.abs(ch1_c))), "Istd_adc": float(np.std(ch1_c)),
                "crest_factor_i": float(ipeak/irms) if irms>EPS else 0.0,
                "P_proxy": p_proxy, "Pabs_mean_proxy": float(np.mean(np.abs(p_inst))),
                "Ppeak_proxy": float(np.max(np.abs(p_inst))), "Pstd_proxy": float(np.std(p_inst)),
                "fs_actual": fs, "n_samples": len(ch1)
            }

            x = ch1_c - np.mean(ch1_c)
            xw = x * np.hanning(len(x))
            mags = np.abs(np.fft.rfft(xw))
            freqs = np.fft.rfftfreq(len(xw), d=1.0/fs)
            
            def get_mag(target):
                if len(freqs)==0: return 0.0
                return float(mags[np.argmin(np.abs(freqs - target))])
            
            h1 = get_mag(60.0)
            h3, h5, h7 = get_mag(180.0), get_mag(300.0), get_mag(420.0)
            feat.update({
                "H1_60_mag": h1, "H3_180_mag": h3, "H5_300_mag": h5, "H7_420_mag": h7,
                "THD_i": float(np.sqrt(h3**2 + h5**2 + h7**2)/h1) if h1>EPS else 0.0,
                "H3_ratio": h3/h1 if h1>EPS else 0.0, "H5_ratio": h5/h1 if h1>EPS else 0.0,
                "H7_ratio": h7/h1 if h1>EPS else 0.0
            })
            
            valid = freqs >= 60.0
            if np.any(valid):
                feat["fft_peak_freq"] = float(freqs[valid][np.argmax(mags[valid])])
                feat["fft_peak_mag"] = float(np.max(mags[valid]))
            else:
                feat["fft_peak_freq"] = 0.0; feat["fft_peak_mag"] = 0.0

            # 2. 상태 관리 (Baseline & ON/OFF)
            self.frame_count += 1
            if self.frame_count <= BASELINE_FRAMES:
                self.baseline_rows.append(feat)
                if self.frame_count == BASELINE_FRAMES:
                    b_df = pd.DataFrame(self.baseline_rows)
                    self.baseline_irms, self.baseline_p = b_df["Irms_adc"].mean(), b_df["P_proxy"].mean()
                    self.thr_i = max(b_df["Irms_adc"].std(ddof=0)*THRESHOLD_SIGMA_I, MIN_THRESHOLD_I)
                    self.thr_p = max(b_df["P_proxy"].std(ddof=0)*3.0, 5000.0)
                return

            feat["baseline_Irms_adc"] = self.baseline_irms
            feat["baseline_P_proxy"] = self.baseline_p
            
            d_i = irms - self.baseline_irms
            d_p = p_proxy - self.baseline_p
            self.delta_i_history.append(d_i)
            self.delta_p_history.append(d_p)
            
            feat["delta_Irms_adc"] = d_i
            feat["delta_P_proxy"] = d_p
            feat["delta_Irms_adc_avg"] = np.mean(self.delta_i_history)
            feat["delta_P_proxy_avg"] = np.mean(self.delta_p_history)
            feat["thr_Irms_adc"] = self.thr_i
            feat["thr_P_proxy"] = self.thr_p

            if self.current_state == "OFF":
                if abs(feat["delta_Irms_adc_avg"]) >= self.thr_i or abs(feat["delta_P_proxy_avg"]) >= self.thr_p:
                    self.current_state = "ON"
            else:
                if abs(feat["delta_Irms_adc_avg"]) <= self.thr_i*OFF_RATIO and abs(feat["delta_P_proxy_avg"]) <= self.thr_p*OFF_RATIO:
                    self.current_state = "OFF"
                    self.valid_on_buffer.clear()
                    self.prob_history.clear()
                    self.ai_text = "🤖 AI: Device OFF (Waiting)"

            feat["state"] = self.current_state
            feat["auto_level"] = "ON" if self.current_state == "ON" else "OFF"
            feat["is_transient"] = False

            # 3. 추론 실행
            if self.current_state == "ON":
                self.valid_on_buffer.append(feat)
                
                if len(self.valid_on_buffer) == WINDOW_SIZE:
                    df_win = pd.DataFrame(list(self.valid_on_buffer))
                    
                    win_feat = {}
                    for col in NUMERIC_COLS_CANDIDATES:
                        if col in df_win.columns: win_feat.update(safe_stats(df_win[col], col))
                        else: win_feat.update(safe_stats([0], col))
                    
                    win_feat["on_ratio"] = 1.0; win_feat["off_ratio"] = 0.0
                    win_feat["transient_ratio"] = 0.0
                    win_feat["auto_level_nunique"] = 1.0; win_feat["num_rows"] = WINDOW_SIZE
                    
                    df_pred = pd.DataFrame([win_feat]).reindex(columns=self.expected_features, fill_value=0.0)
                    
                    probs = self.model.predict_proba(df_pred)[0]
                    self.prob_history.append(probs)
                    
                    avg_prob = np.mean(np.vstack(self.prob_history), axis=0)
                    confidence = float(np.max(avg_prob)) * 100
                    prediction = self.model.classes_[int(np.argmax(avg_prob))]
                    
                    if confidence >= CONFIDENCE_THRESHOLD * 100:
                        self.ai_text = f"🤖 AI Detect: [{prediction.upper()}] ({confidence:.1f}%)"
                    else:
                        self.ai_text = f"🤖 AI Detect: Unknown"

        except Exception as e:
            pass # UI 크래시 방지용 Fail-safe

# =========================================================
# 업그레이드 2: AI 텍스트를 띄우는 UI
# =========================================================
class AIDashboardUI(DashboardUI):
    def update_frame(self, frame):
        # 💡 원본 화면 그리기 로직 100% 재사용
        artists = super().update_frame(frame)
        
        # 💡 텍스트만 슬쩍 끼워넣기
        if self.engine.get_mode() == 0x01:
            curr_title = self.ax1.get_title().split("  ||  ")[0] 
            self.ax1.set_title(f"{curr_title}  ||  {self.engine.ai_text}", color='yellow')
        elif self.engine.get_mode() == 0x02:
            curr_title = self.ax2.get_title().split("  ||  ")[0]
            self.ax2.set_title(f"{curr_title}  ||  {self.engine.ai_text}", color='yellow')
            
        return artists