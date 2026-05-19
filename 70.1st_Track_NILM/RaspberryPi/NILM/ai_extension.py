#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import joblib
import time
import threading
import numpy as np
import pandas as pd
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from collections import deque

from dsp_engine import DSPEngine
from dashboard_ui import DashboardUI

# =========================================================
# 1. AI Inference Settings
# =========================================================

WINDOW_SIZE = 10
BASELINE_FRAMES = 10
DELTA_SMOOTH_WINDOW = 3

THRESHOLD_SIGMA_I = 3.0
THRESHOLD_SIGMA_P = 3.0

MIN_THRESHOLD_I = 20.0
MIN_THRESHOLD_P = 5000.0

OFF_RATIO = 0.6
EPS = 1e-9

CONFIDENCE_THRESHOLD = 0.50
SECOND_DEVICE_THRESHOLD = 0.15

KNOWN_DEVICE_NAMES = [
    "charger", "cooker", "dryer", "fan", "notebook"
]

NUMERIC_COLS_CANDIDATES = [
    "Vrms_adc", "Irms_adc", "Vpeak_adc", "Ipeak_adc", "Vpp_adc", "Ipp_adc",
    "Iabs_mean_adc", "Istd_adc", "crest_factor_i", "P_proxy", "Pabs_mean_proxy",
    "Ppeak_proxy", "Pstd_proxy", "baseline_Irms_adc", "baseline_P_proxy",
    "delta_Irms_adc", "delta_Irms_adc_avg", "delta_P_proxy", "delta_P_proxy_avg",
    "thr_Irms_adc", "thr_P_proxy", "fs_actual", "n_samples", "H1_60_mag",
    "H3_180_mag", "H5_300_mag", "H7_420_mag", "THD_i", "H3_ratio", "H5_ratio",
    "H7_ratio", "fft_peak_freq", "fft_peak_mag"
]

# =========================================================
# 2. Common Functions
# =========================================================

def clean_signal(x):
    x = np.asarray(x, dtype=np.float64)
    if len(x) == 0: return x
    lo = np.percentile(x, 1)
    hi = np.percentile(x, 99)
    return np.clip(x, lo, hi) if lo < hi else x

def safe_stats(series, prefix):
    s = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if len(s) == 0:
        return {f"{prefix}_mean": 0.0, f"{prefix}_std": 0.0, f"{prefix}_min": 0.0, f"{prefix}_max": 0.0, f"{prefix}_median": 0.0}
    return {
        f"{prefix}_mean": float(s.mean()), f"{prefix}_std": float(s.std(ddof=0)) if len(s) > 1 else 0.0,
        f"{prefix}_min": float(s.min()), f"{prefix}_max": float(s.max()), f"{prefix}_median": float(s.median())
    }

def normalize_label(label):
    return str(label).strip().lower()

def extract_known_devices_from_label(label):
    label = normalize_label(label)
    found = [dev for dev in KNOWN_DEVICE_NAMES if dev in label]
    unique = []
    for dev in found:
        if dev not in unique: unique.append(dev)
    return unique

def pretty_device_name(name):
    if name is None: return "UNKNOWN"
    name = str(name).strip().lower()
    mapping = {"dryer": "DRYER", "fan": "FAN", "charger": "CHARGER", "notebook": "NOTEBOOK", "cooker": "COOKER", "unknown": "EMPTY"}
    return mapping.get(name, name.upper())

def find_model_dir(base_dir):
    candidates = [
        os.path.abspath(os.path.join(base_dir, "..", "..", "Model")),
        os.path.abspath(os.path.join(base_dir, "..", "Model")),
        os.path.abspath(os.path.join(os.getcwd(), "Model")),
        os.path.abspath(os.path.join(os.getcwd(), "..", "Model")),
    ]
    for path in candidates:
        if os.path.exists(os.path.join(path, "rf_device_classifier.joblib")): return path
    return candidates[0]

# =========================================================
# 3. AI Engine
# =========================================================

class AIEngine(DSPEngine):
    def __init__(self, spi_core, buffer_size=150):
        super().__init__(spi_core, buffer_size)

        self.ai_status = "LOADING MODEL..."
        self.ai_confidence = 0.0
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = find_model_dir(base_dir)
        self.model_path = os.path.join(model_dir, "rf_device_classifier.joblib")
        self.feature_info_path = os.path.join(model_dir, "rf_device_features.json")

        self.model = None
        self.expected_features = []

        try:
            if not os.path.exists(self.model_path):
                self.ai_status = "NO MODEL"
                return
            if not os.path.exists(self.feature_info_path):
                self.ai_status = "NO FEATURE INFO"
                return

            self.model = joblib.load(self.model_path)
            with open(self.feature_info_path, "r", encoding="utf-8") as f:
                self.expected_features = json.load(f).get("feature_names", [])

            self.ai_status = "STANDBY (OFF)"
        except Exception:
            self.model = None
            self.ai_status = "LOAD ERROR"

        self.frame_count = 0
        self.baseline_rows = []
        self.baseline_irms, self.baseline_p = 0.0, 0.0
        self.thr_i, self.thr_p = MIN_THRESHOLD_I, MIN_THRESHOLD_P
        
        self.delta_i_history = deque(maxlen=DELTA_SMOOTH_WINDOW)
        self.delta_p_history = deque(maxlen=DELTA_SMOOTH_WINDOW)
        self.valid_on_buffer = deque(maxlen=WINDOW_SIZE)
        self.prob_history = deque(maxlen=3)

        self.current_state = "OFF"
        self.socket_states = ["EMPTY", "EMPTY", "EMPTY", "EMPTY"]

        # 💡 [핵심 복구] 고래-새우 현상을 해결할 기억력 변수들!
        self.active_memory = set()
        self.last_P_proxy = 0.0

    def process_raw_mode(self):
        ch0, ch1, timestamps, fs_actual = super().process_raw_mode()
        if self.model is not None and fs_actual > 0:
            self._run_ai_pipeline(ch0, ch1, fs_actual)
        return ch0, ch1, timestamps, fs_actual

    def _extract_frame_features(self, ch0, ch1, fs):
        ch0_c, ch1_c = clean_signal(ch0), clean_signal(ch1)
        vrms, irms = float(np.sqrt(np.mean(ch0_c**2))), float(np.sqrt(np.mean(ch1_c**2)))
        ipeak = float(np.max(np.abs(ch1_c)))
        p_inst = ch0_c * ch1_c
        
        feat = {
            "Vrms_adc": vrms, "Irms_adc": irms, "Vpeak_adc": float(np.max(np.abs(ch0_c))), 
            "Ipeak_adc": ipeak, "Vpp_adc": float(np.max(ch0_c)-np.min(ch0_c)), "Ipp_adc": float(np.max(ch1_c)-np.min(ch1_c)),
            "Iabs_mean_adc": float(np.mean(np.abs(ch1_c))), "Istd_adc": float(np.std(ch1_c)),
            "crest_factor_i": float(ipeak/irms) if irms>EPS else 0.0,
            "P_proxy": float(np.mean(p_inst)), "Pabs_mean_proxy": float(np.mean(np.abs(p_inst))),
            "Ppeak_proxy": float(np.max(np.abs(p_inst))), "Pstd_proxy": float(np.std(p_inst)),
            "fs_actual": float(fs), "n_samples": int(len(ch1_c))
        }

        x = ch1_c - np.mean(ch1_c)
        if len(x) >= 8 and fs > 0:
            xw = x * np.hanning(len(x))
            mags = np.abs(np.fft.rfft(xw))
            freqs = np.fft.rfftfreq(len(xw), d=1.0/fs)
            
            def get_mag(tf): return float(mags[int(np.argmin(np.abs(freqs - tf)))]) if len(freqs)>0 else 0.0
            h1, h3, h5, h7 = get_mag(60.0), get_mag(180.0), get_mag(300.0), get_mag(420.0)
            
            feat.update({"H1_60_mag": h1, "H3_180_mag": h3, "H5_300_mag": h5, "H7_420_mag": h7,
                         "THD_i": float(np.sqrt(h3**2+h5**2+h7**2)/h1) if h1>EPS else 0.0,
                         "H3_ratio": h3/h1 if h1>EPS else 0.0, "H5_ratio": h5/h1 if h1>EPS else 0.0, "H7_ratio": h7/h1 if h1>EPS else 0.0})
            
            valid = freqs >= 60.0
            if np.any(valid):
                peak_idx = int(np.argmax(mags[valid]))
                feat["fft_peak_freq"], feat["fft_peak_mag"] = float(freqs[valid][peak_idx]), float(mags[valid][peak_idx])
            else:
                feat["fft_peak_freq"], feat["fft_peak_mag"] = 0.0, 0.0
        else:
            feat.update({"H1_60_mag":0.0, "H3_180_mag":0.0, "H5_300_mag":0.0, "H7_420_mag":0.0, "THD_i":0.0, "H3_ratio":0.0, "H5_ratio":0.0, "H7_ratio":0.0, "fft_peak_freq":0.0, "fft_peak_mag":0.0})
        return feat

    def _update_state_features(self, feat):
        self.frame_count += 1
        if self.frame_count <= BASELINE_FRAMES:
            self.baseline_rows.append(feat)
            self.ai_status = f"CALIBRATING... {self.frame_count}/{BASELINE_FRAMES}"
            if self.frame_count == BASELINE_FRAMES:
                b_df = pd.DataFrame(self.baseline_rows)
                self.baseline_irms, self.baseline_p = float(b_df["Irms_adc"].mean()), float(b_df["P_proxy"].mean())
                self.thr_i = max(float(b_df["Irms_adc"].std(ddof=0))*THRESHOLD_SIGMA_I, MIN_THRESHOLD_I)
                self.thr_p = max(float(b_df["P_proxy"].std(ddof=0))*THRESHOLD_SIGMA_P, MIN_THRESHOLD_P)
            return None

        feat["baseline_Irms_adc"], feat["baseline_P_proxy"] = self.baseline_irms, self.baseline_p
        d_i, d_p = feat["Irms_adc"] - self.baseline_irms, feat["P_proxy"] - self.baseline_p
        self.delta_i_history.append(d_i); self.delta_p_history.append(d_p)
        d_i_avg, d_p_avg = float(np.mean(self.delta_i_history)), float(np.mean(self.delta_p_history))
        
        feat.update({"delta_Irms_adc": d_i, "delta_P_proxy": d_p, "delta_Irms_adc_avg": d_i_avg, "delta_P_proxy_avg": d_p_avg, "thr_Irms_adc": self.thr_i, "thr_P_proxy": self.thr_p})

        if self.current_state == "OFF":
            if abs(d_i_avg) >= self.thr_i or abs(d_p_avg) >= self.thr_p: self.current_state = "ON"
        else:
            if abs(d_i_avg) <= self.thr_i*OFF_RATIO and abs(d_p_avg) <= self.thr_p*OFF_RATIO:
                self.current_state = "OFF"
                self.valid_on_buffer.clear()
                self.prob_history.clear()
                self.socket_states = ["EMPTY"] * 4
                self.ai_status, self.ai_confidence = "STANDBY (OFF)", 0.0
                # 💡 [핵심 복구] 꺼졌을 때 기억 리셋
                self.active_memory.clear()
                self.last_P_proxy = 0.0

        feat["state"] = self.current_state
        feat["auto_level"] = "ON" if self.current_state == "ON" else "OFF"
        feat["is_transient"] = False
        return feat

    # 💡 [핵심 복구] 기억력을 활용한 2개 기기 추론 로직
    def _infer_two_devices(self, avg_prob, current_P):
        classes = list(self.model.classes_)
        device_scores = {}
        
        for cls, prob in zip(classes, avg_prob):
            for dev in extract_known_devices_from_label(normalize_label(cls)):
                device_scores[dev] = device_scores.get(dev, 0.0) + float(prob)
                
        if current_P < self.last_P_proxy * 0.90:
            self.active_memory.clear()
        
        power_jumped = False
        if current_P > self.last_P_proxy * 1.05:
            self.last_P_proxy = current_P
            power_jumped = True
        elif current_P < self.last_P_proxy * 0.90:
            self.last_P_proxy = current_P
            
        for dev in list(self.active_memory):
            if dev in device_scores:
                device_scores[dev] += 0.20
                
        sorted_devices = sorted(device_scores.items(), key=lambda x: x[1], reverse=True)
        s1, s2 = "EMPTY", "EMPTY"
        best_conf = 0.0
        
        if len(sorted_devices) > 0:
            s1_cand, s1_score = sorted_devices[0]
            if s1_score >= 0.25:
                s1 = s1_cand
                self.active_memory.add(s1)
                best_conf = s1_score
                
        if len(sorted_devices) > 1:
            s2_cand, s2_score = sorted_devices[1]
            s1_score = sorted_devices[0][1]
            threshold_s2 = 0.10 if power_jumped else SECOND_DEVICE_THRESHOLD
            
            if s2_score >= threshold_s2 and s2_score >= (s1_score * 0.20):
                s2 = s2_cand
                self.active_memory.add(s2)
            else:
                if s2_cand in self.active_memory:
                    self.active_memory.remove(s2_cand)

        return s1, s2, "tracked", best_conf

    def _run_ai_pipeline(self, ch0, ch1, fs):
        try:
            feat = self._update_state_features(self._extract_frame_features(ch0, ch1, fs))
            if feat is None or self.current_state != "ON": return
            
            self.valid_on_buffer.append(feat)
            if len(self.valid_on_buffer) < WINDOW_SIZE:
                self.ai_status = f"ANALYZING... {len(self.valid_on_buffer)}/{WINDOW_SIZE}"
                return

            df_win = pd.DataFrame(list(self.valid_on_buffer))
            win_feat = {}
            for col in NUMERIC_COLS_CANDIDATES: win_feat.update(safe_stats(df_win[col], col) if col in df_win.columns else safe_stats([0.0], col))
            win_feat.update({"on_ratio":1.0, "off_ratio":0.0, "transient_ratio":0.0, "auto_level_nunique":1.0, "num_rows":float(WINDOW_SIZE)})
            
            df_pred = pd.DataFrame([win_feat]).reindex(columns=self.expected_features, fill_value=0.0).apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
            self.prob_history.append(self.model.predict_proba(df_pred)[0])
            avg_prob = np.mean(np.vstack(self.prob_history), axis=0)

            # 💡 [핵심 복구] 추론 함수에 전력값(P_proxy) 넘겨주기
            current_P = win_feat.get("P_proxy_mean", 0.0)
            s1, s2, best_label, best_conf = self._infer_two_devices(avg_prob, current_P)
            
            self.ai_confidence = best_conf * 100.0

            if best_conf >= CONFIDENCE_THRESHOLD:
                self.socket_states = [pretty_device_name(s1), pretty_device_name(s2), "EMPTY", "EMPTY"]
                self.ai_status = "DETECTED"
            else:
                self.ai_status = "LOW CONFIDENCE"
        except Exception:
            pass

# =========================================================
# 4. New AI Dashboard UI (Grid Layout)
# =========================================================

class AIDashboardUI(DashboardUI):
    def __init__(self, dsp_engine):
        self.engine = dsp_engine
        self.buffer_size = self.engine.buffer_size
        self.fft_x_hz = np.arange(1, 17) * 30.0

        # 💡 좌측 1칸, 우측 2칸 비율로 화면 분할
        self.fig = plt.figure(figsize=(12, 8))
        self.fig.canvas.manager.set_window_title('WattsUp AI Dashboard')
        self.fig.patch.set_facecolor('#1e1e1e')
        gs = gridspec.GridSpec(2, 3, figure=self.fig)

        # 💡 [왼쪽 섹션] 소켓 상태 표시 패널 (전체 높이 차지)
        self.ax_info = self.fig.add_subplot(gs[:, 0])
        self.ax_info.set_facecolor('#121212')
        self.ax_info.axis('off') # 축 숨기기
        
        # 소켓 텍스트를 담을 객체 리스트 초기화
        self.info_texts = []
        self._init_info_panel()

        # 💡 [오른쪽 상단] 오실로스코프 (Time Domain)
        self.ax1 = self.fig.add_subplot(gs[0, 1:])
        self.line_ch0, = self.ax1.plot(np.zeros(self.buffer_size), label='Voltage(PT)', color='magenta', linewidth=1.5)
        self.line_ch1, = self.ax1.plot(np.zeros(self.buffer_size), label='Current(CT)', color='cyan', linewidth=1.5)
        self.ax1.set_ylim(-2048, 2048)
        self.ax1.set_xlim(0, self.buffer_size)
        self.ax1.legend(loc='upper right', facecolor='black', edgecolor='gray', labelcolor='white')
        self.ax1.grid(True, linestyle='--', alpha=0.3)
        self.ax1.set_facecolor('black')

        # 💡 [오른쪽 하단] FFT 스펙트럼 (Frequency Domain)
        self.ax2 = self.fig.add_subplot(gs[1, 1:])
        self.bars = self.ax2.bar(self.fft_x_hz, np.zeros(16), color='lime', width=15)
        self.ax2.set_xlim(0, 500)
        self.ax2.set_ylim(0, 10000)
        target_freqs = [60, 180, 300, 420]
        self.ax2.set_xticks(target_freqs)
        self.ax2.set_xticklabels([f"{f}Hz" for f in target_freqs], color='yellow', fontweight='bold')
        self.ax2.grid(True, axis='x', color='yellow', linestyle=':', alpha=0.5)
        self.ax2.grid(True, axis='y', linestyle='--', alpha=0.3)
        self.ax2.set_facecolor('black')

        # 전체 테마 및 이벤트 적용
        for ax in [self.ax1, self.ax2]:
            ax.tick_params(colors='white')
            for spine in ax.spines.values(): spine.set_edgecolor('gray')
        
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.ax1.set_alpha(1.0)
        self.ax2.set_alpha(0.2)

    def _init_info_panel(self):
        """왼쪽 패널의 텍스트 레이아웃을 초기화합니다."""
        self.ax_info.text(0.05, 0.95, "SMART MULTITAP", color='white', fontsize=18, fontweight='bold', transform=self.ax_info.transAxes)
        self.ax_info.text(0.05, 0.90, "AI NILM SYSTEM", color='cyan', fontsize=12, transform=self.ax_info.transAxes)
        
        self.status_text = self.ax_info.text(0.05, 0.80, "STATUS: WAIT", color='yellow', fontsize=14, transform=self.ax_info.transAxes)
        self.conf_text = self.ax_info.text(0.05, 0.75, "CONFIDENCE: 0.0%", color='lightgray', fontsize=12, transform=self.ax_info.transAxes)
        
        self.ax_info.text(0.05, 0.60, "[ CONNECTED DEVICES ]", color='white', fontsize=12, transform=self.ax_info.transAxes)
        
        # 소켓 1~4 텍스트 객체 생성
        for i in range(4):
            y_pos = 0.50 - (i * 0.1)
            txt = self.ax_info.text(0.05, y_pos, f"Socket {i+1}: EMPTY", color='lime', fontsize=14, fontweight='bold', transform=self.ax_info.transAxes)
            self.info_texts.append(txt)

    def update_frame(self, frame):
        # 💡 왼쪽 정보 패널 업데이트
        self.status_text.set_text(f"STATUS: {self.engine.ai_status}")
        self.conf_text.set_text(f"CONF: {self.engine.ai_confidence:.1f}%")
        
        for i in range(4):
            state = self.engine.socket_states[i]
            color = 'lime' if state != "EMPTY" else 'gray'
            self.info_texts[i].set_text(f"Socket {i+1}: {state}")
            self.info_texts[i].set_color(color)

        # 💡 오른쪽 파형 패널 업데이트
        current_mode = self.engine.get_mode()
        artists = [self.status_text, self.conf_text] + self.info_texts

        if current_mode == 0x01:
            ch0, ch1, timestamps, fs_actual = self.engine.process_raw_mode()
            self.line_ch0.set_ydata(ch0)
            self.line_ch1.set_ydata(ch1)
            self.ax1.set_title(f"Oscilloscope (fs={fs_actual:.1f}Hz) [Press '1']", color='white')
            self.ax2.set_title(f"Harmonic Spectrum [Press '2']", color='gray')
            artists.extend([self.line_ch0, self.line_ch1])

        elif current_mode == 0x02:
            new_fft_y = self.engine.process_fft_mode()
            for bar, h in zip(self.bars, new_fft_y): bar.set_height(h)
            max_val = np.max(new_fft_y) if len(new_fft_y) > 0 else 0
            self.ax2.set_ylim(0, max_val * 1.2 if max_val > 100 else 1000)
            
            if len(new_fft_y) > 0:
                peak_idx = int(np.argmax(new_fft_y))
                self.ax2.set_title(f"Spectrum: Peak {float(self.fft_x_hz[peak_idx]):.1f}Hz [Press '2']", color='white')
            self.ax1.set_title(f"Oscilloscope [Press '1']", color='gray')
            artists.extend(self.bars)

        return artists