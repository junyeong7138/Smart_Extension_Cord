#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import joblib
import numpy as np
import pandas as pd
from collections import deque
import logging  # 💡 [추가] 로그 라이브러리
from datetime import datetime  # 💡 [추가] 시간 기록용
from dsp_engine import DSPEngine
from dashboard_ui import DashboardUI

# 💡 [추가] 로그 파일 생성 설정 (실행할 때마다 파일이름에 시간이 찍힘)
logging.basicConfig(
    filename=f"nilm_test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)

# =========================================================
# 1. AI 추론 설정 (★ 현장 튜닝 필수 값)
# =========================================================
WINDOW_SIZE = 10
# 💡 [수정] 선풍기 통과를 위해 문턱을 대폭 낮춤 (기존 3000 -> 500)
MIN_THRESHOLD_P = 500.0         
# 💡 [수정] 전류 문턱도 낮춤 (기존 10 -> 2)
MIN_THRESHOLD_I = 2.0           
PROPORTIONAL_THR_RATIO = 0.04   
EVENT_COOLDOWN_FRAMES = 15      
MIN_CONFIDENCE = 0.45

def find_model_dir():
    base = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()
    paths = [
        os.path.join(base, "Model"),
        os.path.join(base, "..", "Model"),
        os.path.join(base, "..", "..", "Model"),
        os.path.join(cwd, "Model"),
        os.path.join(cwd, "..", "Model"),
        os.path.join(cwd, "..", "..", "Model")
    ]
    for p in paths:
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "rf_device_classifier.joblib")):
            return p
    return base

# =========================================================
# 2. AIEngine
# =========================================================
class AIEngine(DSPEngine):
    def __init__(self, spi_core, buffer_size=150, model_path=None, feature_info_path=None):
        super().__init__(spi_core, buffer_size)
        
        if model_path is None or feature_info_path is None:
            mdir = find_model_dir()
            model_path = os.path.join(mdir, "rf_device_classifier.joblib")
            feature_info_path = os.path.join(mdir, "rf_device_features.json")

        try:
            self.model = joblib.load(model_path)
            with open(feature_info_path, "r", encoding="utf-8") as f:
                info = json.load(f)
                self.expected_features = info["feature_names"]
                self.device_prototypes = info.get("device_prototypes", {})
            self.ai_ready = True
        except Exception as e:
            print(f"[AI INIT ERROR] 모델 로드 실패: {e}")
            self.ai_ready = False

        self.active_devices = []
        # 💡 [이렇게 변경/추가] 소켓 위치와 과거 상태를 기억하는 메모리 변수들
        self.socket_states = ["EMPTY", "EMPTY", "EMPTY", "EMPTY"]
        self.socket_memory = {}  # 예: {'dryer': 0, 'fan': 1} (어떤 기기가 몇 번 소켓에 꽂혔었는지 기억)
        self.next_socket_idx = 0

        self.stable_ref_feat = None
        self.event_cooldown = 0
        self.ai_text = "🤖 AI: READY"
        self.frame_buffer = deque(maxlen=WINDOW_SIZE)
        self.debug_frame_cnt = 0

    def process_raw_mode(self, *args, **kwargs):
        ret = super().process_raw_mode(*args, **kwargs)
        if ret is None or len(ret) < 4:
            return ret
            
        ch0, ch1, timestamps, fs_actual = ret[:4]
        
        if self.ai_ready:
            frame_feat = self._extract_frame_features(ch0, ch1, fs_actual)
            self.frame_buffer.append(frame_feat)
            
            if len(self.frame_buffer) == WINDOW_SIZE:
                win_feat = self._create_window_features(list(self.frame_buffer))
                self._process_delta_tracking(win_feat)

        return ret

    def _extract_frame_features(self, ch0, ch1, fs):
        c0 = np.asarray(ch0, dtype=np.float64)
        c1 = np.asarray(ch1, dtype=np.float64)
        
        if len(c0) > 0:
            lo0, hi0 = np.percentile(c0, 1), np.percentile(c0, 99)
            if lo0 < hi0: c0 = np.clip(c0, lo0, hi0)
        
        if len(c1) > 0:
            lo1, hi1 = np.percentile(c1, 1), np.percentile(c1, 99)
            if lo1 < hi1: c1 = np.clip(c1, lo1, hi1)

        vrms = np.sqrt(np.mean(c0**2)) if len(c0) > 0 else 0.0
        irms = np.sqrt(np.mean(c1**2)) if len(c1) > 0 else 0.0

        p_inst = c0 * c1
        p_proxy = np.mean(p_inst) if len(p_inst) > 0 else 0.0
        
        pabs_mean_proxy = float(np.mean(np.abs(p_inst))) if len(p_inst) > 0 else 0.0
        pstd_proxy = float(np.std(p_inst)) if len(p_inst) > 0 else 0.0
        ipeak = float(np.max(np.abs(c1))) if len(c1) > 0 else 0.0
        crest_factor_i = float(ipeak / irms) if irms > 1e-9 else 0.0
        
        # 💡 [핵심 복원] FPGA의 64-point FFT를 똑같이 재현하여 AI의 주파수 시력을 살려냅니다!
        h1 = h3 = h5 = h7 = thd = 0.0
        if len(c1) >= 64 and fs > 0:
            c1_64 = c1[-64:] 
            x = c1_64 - np.mean(c1_64) 
            mags = np.abs(np.fft.rfft(x))
            if len(mags) > 14:
                h1 = float(mags[2])
                h3 = float(mags[6])
                h5 = float(mags[10])
                h7 = float(mags[14])
                if h1 > 1e-9: 
                    thd = np.sqrt(h3**2 + h5**2 + h7**2) / h1

        return {
            "Vrms_adc": vrms, "Irms_adc": irms, "P_proxy": p_proxy,
            "Pabs_mean_proxy": pabs_mean_proxy, "Pstd_proxy": pstd_proxy,
            "crest_factor_i": crest_factor_i,
            "H1_60_mag": h1, "H3_180_mag": h3, "H5_300_mag": h5, "H7_420_mag": h7, "THD_i": thd
        }

    def _create_window_features(self, frames):
        df = pd.DataFrame(frames)
        win_feat = {}
        for col in df.columns:
            win_feat[f"{col}_mean"] = float(df[col].mean())
            win_feat[f"{col}_std"] = float(df[col].std(ddof=0))
        return win_feat

    def _process_delta_tracking(self, win_feat):
        try:
            def get_real_p(d):
                if d == "cooker": return 163000.0
                if d == "dryer": return 100000.0 
                if d == "charger": return 5000.0
                return 4400.0 # fan

            if not hasattr(self, 'current_device_p'): 
                self.current_device_p = {}

            if "airfryer" in self.active_devices:
                self.active_devices.remove("airfryer")

            curr_pabs = win_feat.get("Pabs_mean_proxy_mean", 0.0)
            curr_p = win_feat.get("P_proxy_mean", 0.0)
            curr_i = win_feat.get("Irms_adc_mean", 0.0)

            self.debug_frame_cnt += 1
            if self.debug_frame_cnt < 30:
                self.stable_ref_feat = win_feat
                return

            if curr_pabs < MIN_THRESHOLD_P and curr_i < MIN_THRESHOLD_I:
                if self.active_devices:
                    logging.info(f"🔴 [OFF GATE] 전력 바닥침. 모든 기기 OFF.")
                    removed_list = list(self.active_devices)
                    self.active_devices = []
                    self.current_device_p = {}
                    for dev in removed_list:
                        self._update_ui_text(removed_dev=dev)
                self.stable_ref_feat = win_feat
                return

            if self.event_cooldown > 0:
                self.event_cooldown -= 1
                return

            curr_pabs_std = win_feat.get("Pabs_mean_proxy_std", 0.0)
            if curr_pabs_std > max(MIN_THRESHOLD_P * 1.5, curr_pabs * 0.20):
                return

            if self.stable_ref_feat is None:
                self.stable_ref_feat = win_feat
                return

            ref_pabs = self.stable_ref_feat.get("Pabs_mean_proxy_mean", 0.0)
            ref_p = self.stable_ref_feat.get("P_proxy_mean", 0.0)
            ref_i = self.stable_ref_feat.get("Irms_adc_mean", 0.0)
            
            delta_p = curr_p - ref_p
            delta_pabs = curr_pabs - ref_pabs
            delta_i = curr_i - ref_i
            
            ref_noise = self.stable_ref_feat.get("Pabs_mean_proxy_std", 0.0)
            dynamic_thr = min(max(MIN_THRESHOLD_P, ref_noise * 2.0), 3500.0)

            # ==========================================
            # 3. ADD 이벤트 (켜짐)
            # ==========================================
            if delta_p > dynamic_thr or delta_pabs > dynamic_thr:
                if delta_i < MIN_THRESHOLD_I * 0.5:
                    self._handle_plug_spark("IN") # 💡 플러그 IN 스파크 캐치!
                    return 
                
                delta_feat = {k: win_feat[k] - self.stable_ref_feat.get(k, 0.0) 
                            for k in self.expected_features if k in win_feat}
                pred, conf = self._predict_delta(delta_feat)
                
                if conf >= MIN_CONFIDENCE:
                    measured_p = max(abs(delta_p), abs(delta_pabs))
                    
                    if measured_p < 1500.0:
                        logging.info(f"🛡️ [노이즈 컷] 전력 미달({measured_p:.1f}W). 스파크 무시!")
                        self._handle_plug_spark("IN") # 💡 플러그 IN 스파크 캐치!
                    else:
                        if pred in ["fan", "charger"] and measured_p > 50000.0:
                            best_heavy = min(["dryer", "cooker"], key=lambda d: abs(get_real_p(d) - measured_p))
                            logging.info(f"🔄 [교정] 전력이 너무 큼({measured_p:.1f}W). {pred.upper()} -> {best_heavy.upper()}")
                            pred = best_heavy

                        elif pred in ["dryer", "cooker"] and measured_p < 15000.0:
                            if pred not in self.active_devices:
                                logging.info(f"🛡️ [전력 컷] {pred} 라기엔 전력({measured_p:.1f}W)이 너무 작음. 스파크 무시!")
                                self._handle_plug_spark("IN") # 💡 플러그 IN 스파크 캐치!
                                return

                        elif pred in self.active_devices and measured_p > 50000.0:
                            best_heavy = min(["dryer", "cooker"], key=lambda d: abs(get_real_p(d) - measured_p))
                            if best_heavy not in self.active_devices:
                                logging.info(f"🔄 [교정] 엄청난 전력({measured_p:.1f}W). 새로운 {best_heavy.upper()} 켜짐 간주!")
                                pred = best_heavy

                        if pred in ["fan", "charger"] and not (2500.0 < measured_p < 8800.0):
                            logging.info(f"🛡️ [전력 컷] {pred} 정상 전력(2.5k~7.5k)을 벗어남({measured_p:.1f}W). 스파크 무시!")
                            self._handle_plug_spark("IN") # 💡 플러그 IN 스파크 캐치!
                            return

                        if "cooker" in self.active_devices and 60000.0 < measured_p < 95000.0:
                            pred = "cooker"
                            logging.info(f"🔄 [사이클] 밥통 재가열 감지({measured_p:.1f}W)!")

                        required_i = 0.5 if pred in ["fan", "charger"] else 5.0
                        if delta_i < required_i:
                            logging.info(f"🛡️ [전류 컷] 전류 부족 -> 가짜 노이즈 차단!")
                            self._handle_plug_spark("IN") # 💡 플러그 IN 스파크 캐치!
                        elif pred not in self.active_devices:
                            self.active_devices.append(pred)
                            self.current_device_p[pred] = measured_p
                            logging.info(f"🟢 [ADD EVENT] '{pred.upper()}' 켜짐! (변화량: {measured_p:.1f}W)")
                            self._update_ui_text()
                        else:
                            self.current_device_p[pred] = self.current_device_p.get(pred, 0) + measured_p
                            logging.info(f"🔄 [모드 변경/사이클] '{pred.upper()}' 전력 증가 (+{measured_p:.1f}W). 유지!")
                
                self.stable_ref_feat = win_feat
                self.event_cooldown = EVENT_COOLDOWN_FRAMES

            # ==========================================
            # 4. REMOVE 이벤트 (꺼짐)
            # ==========================================
            elif delta_p < -dynamic_thr or delta_pabs < -dynamic_thr:
                if delta_i > -MIN_THRESHOLD_I * 0.5:
                    self._handle_plug_spark("OUT") # 💡 플러그 OUT 스파크 캐치!
                    return 
                
                dropped_p = abs(delta_p) if abs(delta_p) > dynamic_thr else abs(delta_pabs)
                
                if dropped_p < 1500.0:
                    logging.info(f"🛡️ [노이즈 컷] 미세 전력 감소 ({dropped_p:.1f}W). 스파크 차단!")
                    self._handle_plug_spark("OUT") # 💡 플러그 OUT 스파크 캐치!
                else:
                    dropped_i = abs(win_feat.get("Irms_adc_mean", 0.0) - self.stable_ref_feat.get("Irms_adc_mean", 0.0))
                    
                    delta_feat = {k: self.stable_ref_feat.get(k, 0.0) - win_feat.get(k, 0.0) 
                                for k in self.expected_features if k in win_feat}
                    pred, conf = self._predict_delta(delta_feat)
                    removed_dev = pred
                    
                    if removed_dev in ["fan", "charger"] and dropped_p > 50000.0:
                        removed_dev = min([d for d in ["dryer", "cooker"] if d in self.active_devices], 
                                          key=lambda d: abs(get_real_p(d) - dropped_p), default=removed_dev)

                    elif removed_dev in ["dryer", "cooker"] and dropped_p < 15000.0:
                        if removed_dev not in self.active_devices:
                            removed_dev = min([d for d in ["fan", "charger"] if d in self.active_devices], 
                                              key=lambda d: abs(get_real_p(d) - dropped_p), default=None)
                            if not removed_dev: 
                                self._handle_plug_spark("OUT") # 💡 플러그 OUT 스파크 캐치!
                                return 

                    elif removed_dev in self.active_devices and dropped_p > 50000.0:
                        best_heavy = min([d for d in ["dryer", "cooker"] if d in self.active_devices], 
                                         key=lambda d: abs(get_real_p(d) - dropped_p), default=removed_dev)
                        removed_dev = best_heavy

                    if "cooker" in self.active_devices and 60000.0 < dropped_p < 95000.0:
                        removed_dev = "cooker"

                    if removed_dev not in self.active_devices:
                        best_active = min(self.active_devices, key=lambda d: abs(get_real_p(d) - dropped_p), default=None)
                        if best_active:
                            if get_real_p(best_active) > 50000 and dropped_p < 15000:
                                removed_dev = best_active
                            elif get_real_p(best_active) < 15000 and dropped_p < 15000:
                                removed_dev = best_active
                            elif get_real_p(best_active) > 50000 and dropped_p > 50000:
                                removed_dev = best_active
                    
                    if removed_dev:
                        current_p = self.current_device_p.get(removed_dev, get_real_p(removed_dev))
                        
                        if dropped_p < current_p * 0.7:
                            self.current_device_p[removed_dev] = max(0, current_p - dropped_p)
                            logging.info(f"🔄 [모드 변경/사이클] '{removed_dev}' 전력 감소 (-{dropped_p:.1f}W). 유지!")
                        else:
                            required_i_rem = 0.5 if removed_dev in ["fan", "charger"] else 5.0
                            if dropped_i < required_i_rem:
                                logging.info(f"🛡️ [전류 컷] 꺼짐 노이즈 차단!")
                                self._handle_plug_spark("OUT") # 💡 플러그 OUT 스파크 캐치!
                            else:
                                self.active_devices.remove(removed_dev)
                                if removed_dev in self.current_device_p:
                                    del self.current_device_p[removed_dev]
                                logging.info(f"🔴 [REMOVE EVENT] '{removed_dev.upper()}' 꺼짐! (-{dropped_p:.1f}W)")
                                self._update_ui_text(removed_dev=removed_dev)
                
                self.stable_ref_feat = win_feat
                self.event_cooldown = EVENT_COOLDOWN_FRAMES

            # ==========================================
            # 5. 미세 변동 & 6. Sanity Check
            # ==========================================
            else:
                alpha = 0.1
                for k in self.expected_features:
                    if k in win_feat and k in self.stable_ref_feat:
                        self.stable_ref_feat[k] = (1 - alpha) * self.stable_ref_feat[k] + alpha * win_feat[k]
            
            if self.active_devices and self.event_cooldown == 0:
                real_expected_p = sum(self.current_device_p.get(d, 0) for d in self.active_devices)
                diff_p = real_expected_p - curr_pabs
                
                if self.active_devices:
                    smallest_p = min(self.current_device_p.get(d, 999999) for d in self.active_devices)
                    if diff_p > (smallest_p * 0.7) and diff_p > 3000.0: 
                        ghost_dev = min(self.active_devices, key=lambda d: abs(self.current_device_p.get(d, 0) - diff_p))
                        logging.info(f"👻 [Sanity Check] '{ghost_dev}' 몰래 꺼짐! ({diff_p:.1f}W 비어있음)")
                        self.active_devices.remove(ghost_dev)
                        if ghost_dev in self.current_device_p:
                            del self.current_device_p[ghost_dev]
                        self._update_ui_text(removed_dev=ghost_dev)
                        self.event_cooldown = EVENT_COOLDOWN_FRAMES

        except Exception as e:
            print("[AI TRK ERROR]", e)

    def _predict_delta(self, feat_dict):
        df_input = pd.DataFrame([feat_dict]).reindex(columns=self.expected_features, fill_value=0.0)
        probs = self.model.predict_proba(df_input)[0]
        idx = np.argmax(probs)
        return self.model.classes_[idx], probs[idx]

    def _find_closest_device_to_remove(self, d_p, d_i, d_h1):
        if not self.active_devices: return None
        best_dev, min_dist = None, float('inf')
        for dev in self.active_devices:
            proto = self.device_prototypes.get(dev, {"P_proxy": 0, "Irms_adc": 0, "H1_60_mag": 0})
            dist = np.sqrt(
                ((proto.get("P_proxy", 0) - d_p) / 5000.0)**2 + 
                ((proto.get("Irms_adc", 0) - d_i) / 20.0)**2 +
                ((proto.get("H1_60_mag", 0) - d_h1) / 100.0)**2
            )
            if dist < min_dist:
                min_dist = dist; best_dev = dev
        return best_dev

    # 💡 [새로 추가] 플러그 IN/OUT 스파크를 감지하여 UI에 반영하는 함수
    def _handle_plug_spark(self, action):
        if action == "IN":
            # EMPTY나 PLUG_OUT 인 소켓을 찾아 PLUG_IN으로 변경
            for i in range(4):
                if self.socket_states[i] in ["EMPTY", "PLUG_OUT"]:
                    self.socket_states[i] = "PLUG_IN"
                    logging.info(f"🔌 [플러그 감지] 소켓 {i+1}번에 코드가 꽂혔습니다! (PLUG_IN)")
                    self.event_cooldown = EVENT_COOLDOWN_FRAMES
                    break
        elif action == "OUT":
            # OFF로 대기 중인 기기나, 꽂혀만 있던(PLUG_IN) 소켓을 찾아 PLUG_OUT으로 변경
            for i in range(4):
                if self.socket_states[i].endswith("_OFF") or self.socket_states[i] == "PLUG_IN":
                    old_state = self.socket_states[i]
                    self.socket_states[i] = "PLUG_OUT"
                    logging.info(f"🔌 [플러그 감지] 소켓 {i+1}번({old_state}) 코드가 뽑혔습니다! (PLUG_OUT)")
                    
                    # 메모리에서도 제거하여 다음 기기가 빈자리로 쓸 수 있게 비워줌
                    dev_to_del = None
                    for dev, idx in self.socket_memory.items():
                        if idx == i:
                            dev_to_del = dev
                    if dev_to_del:
                        del self.socket_memory[dev_to_del]
                        
                    self.event_cooldown = EVENT_COOLDOWN_FRAMES
                    break

    def _update_ui_text(self, removed_dev=None):
        # 1. 현재 켜져 있는 기기들 업데이트 (ON)
        for dev in self.active_devices:
            if dev not in self.socket_memory:
                assigned = False
                # 최우선: 방금 꽂은 플러그(PLUG_IN)가 있는 자리를 할당
                for i in range(4):
                    if self.socket_states[i] == "PLUG_IN":
                        self.socket_memory[dev] = i
                        assigned = True
                        break
                
                # 차선: 만약 스파크를 놓쳤다면 EMPTY나 PLUG_OUT 인 자리를 찾아 할당
                if not assigned:
                    for i in range(4):
                        if self.socket_states[i] in ["EMPTY", "PLUG_OUT"] or self.socket_states[i].endswith("_OFF"):
                            self.socket_memory[dev] = i
                            assigned = True
                            break
                            
            if dev in self.socket_memory:
                s_idx = self.socket_memory[dev]
                self.socket_states[s_idx] = f"{dev.upper()}_ON"

        # 2. 방금 꺼진 기기 업데이트 (OFF)
        if removed_dev and removed_dev in self.socket_memory:
            s_idx = self.socket_memory[removed_dev]
            self.socket_states[s_idx] = f"{removed_dev.upper()}_OFF"

        self.ai_text = f"🤖 AI: {' + '.join(self.active_devices).upper()}" if self.active_devices else "🤖 AI: STANDBY"
        
        logging.info(f"📺 [UI 화면 갱신] 장부: {self.active_devices} | 소켓화면: {self.socket_states}")

# =========================================================
# 3. AIDashboardUI
# =========================================================
class AIDashboardUI(DashboardUI):
    def __init__(self, *args, **kwargs):
        # 부모 클래스의 기본 화면 세팅을 먼저 불러옵니다
        super().__init__(*args, **kwargs)
        
        # 💡 [핵심] 오실로스코프 화면을 우측으로 밀어냅니다 (왼쪽에 30%의 여백 확보)
        self.fig.subplots_adjust(left=0.3)
        
        # 확보된 왼쪽 공간에 '타이틀'과 '소켓(1~4)' 텍스트 UI를 생성합니다
        self.fig.text(0.03, 0.9, "🔌 AI MULTITAP", color='cyan', fontsize=18, fontweight='bold')
        
        self.socket_texts = []
        for i in range(4):
            # y축 위치를 0.7부터 아래로 0.18씩 띄워가며 4개의 소켓 텍스트 배치
            txt = self.fig.text(0.03, 0.7 - (i * 0.18), f"[ Socket {i+1} ]\nEMPTY", 
                                color='gray', fontsize=15, fontweight='bold')
            self.socket_texts.append(txt)

    def update_frame(self, frame):
        artists = super().update_frame(frame)
        
        if hasattr(self, 'engine') and hasattr(self.engine, 'socket_states'):
            for i in range(4):
                state = self.engine.socket_states[i]
                color = 'lime' if state != "EMPTY" else 'gray'
                
                # 💡 [여기 수정] EMPTY일 때 회색으로 'PLUGGED_OFF'라고 띄워줍니다!
                display_text = "PLUGGED_OFF" if state == "EMPTY" else state
                
                self.socket_texts[i].set_text(f"[ Socket {i+1} ]\n{display_text}")
                self.socket_texts[i].set_color(color)
                
                if isinstance(artists, list):
                    artists.append(self.socket_texts[i])

                    
        # (기존) 상단 타이틀에 전체 AI 추론 상태 띄우기
        if hasattr(self, 'ax1') and hasattr(self, 'engine') and hasattr(self.engine, 'ai_text'):
            curr_title = self.ax1.get_title().split("  ||  ")[0]
            self.ax1.set_title(f"{curr_title}  ||  {self.engine.ai_text}", color="yellow")
            
        return artists