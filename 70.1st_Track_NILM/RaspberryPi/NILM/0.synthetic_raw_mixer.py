#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
import datetime
import numpy as np
import pandas as pd
import itertools

# =========================================================
# 1. 경로 설정 (사용자 요구사항 반영)
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 참조할 단일 기기 데이터 경로 (../../00.Docs/Data/once)
RAW_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "once"))

# 합성된 데이터를 저장할 경로 (../../Data/Fake_Multi_Raw)
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "Data", "Fake_Multi_Raw"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def mix_and_save(path_a, path_b, combo_idx, total_combos):
    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)

    dev_a, dev_b = str(df_a["device"].iloc[0]).lower(), str(df_b["device"].iloc[0]).lower()
    mode_a, mode_b = str(df_a["mode"].iloc[0]).upper(), str(df_b["mode"].iloc[0]).upper()
    
    devices = sorted([dev_a, dev_b])
    new_device = f"{devices[0]}_{devices[1]}"
    new_mode = f"{mode_a}_{mode_b}" if devices[0] == dev_a else f"{mode_b}_{mode_a}"

    print(f"[{combo_idx}/{total_combos}] 🛠️ 믹스 중: [{new_device.upper()}] - {new_mode}")

    df_mixed = pd.merge(df_a, df_b, on=['frame_index', 'sample_or_bin_index'], suffixes=('_a', '_b'))
    if df_mixed.empty: return False

    df_mixed = df_mixed.sort_values(['frame_index', 'sample_or_bin_index'])

    v_a = df_mixed['ch0_adc_centered_a'].values
    i_a = df_mixed['ch1_adc_centered_a'].values
    i_b = df_mixed['ch1_adc_centered_b'].values

    # 통짜 위상 동기화 로직
    search_len = min(2000, len(v_a))
    v_a_sub = v_a[:search_len] - np.mean(v_a[:search_len])
    v_b_sub = df_mixed['ch0_adc_centered_b'].values[:search_len] - np.mean(df_mixed['ch0_adc_centered_b'].values[:search_len])

    if np.std(v_a_sub) > 1e-5 and np.std(v_b_sub) > 1e-5:
        corr = np.correlate(v_a_sub, v_b_sub, mode='full')
        lag = np.argmax(corr) - (len(v_b_sub) - 1)
        i_b_aligned = np.roll(i_b, lag)
    else:
        i_b_aligned = i_b

    # 전압 강하 예방접종 (100% 버전과 90% 버전 생성)
    scales = [1.0, 0.90]
    
    for scale in scales:
        run_id_scaled = f"synth_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{combo_idx:04d}_s{int(scale*100)}"
        
        i_synth = (i_a + i_b_aligned) * scale
        v_synth = v_a * scale
        
        time_out = pd.DataFrame({
            "run_id": run_id_scaled, "device": new_device, "mode": new_mode, "record_type": "time",
            "frame_index": df_mixed['frame_index'], "sample_or_bin_index": df_mixed['sample_or_bin_index'],
            "timestamp": df_mixed['timestamp_a'], 
            "ch0_adc_centered": v_synth, 
            "ch1_adc_centered": i_synth, 
            "frequency_hz": "", "fft_magnitude": "",
            "fs_actual": df_mixed['fs_actual_a']
        })

        fft_rows = []
        fft_freqs_hz = np.arange(1, 17) * 30.0

        for frame_idx, group in time_out.groupby('frame_index'):
            ch1_wave = group['ch1_adc_centered'].values
            fs = float(group['fs_actual'].iloc[0])
            if len(ch1_wave) < 16 or fs <= 0: continue
                
            x = ch1_wave - np.mean(ch1_wave)
            xw = x * np.hanning(len(x))
            mags = np.abs(np.fft.rfft(xw))
            freqs = np.fft.rfftfreq(len(xw), d=1.0/fs)
            ts = group['timestamp'].iloc[0]
            
            for bin_idx, target_f in enumerate(fft_freqs_hz):
                nearest_mag = float(mags[np.argmin(np.abs(freqs - target_f))])
                fft_rows.append({
                    "run_id": run_id_scaled, "device": new_device, "mode": new_mode, "record_type": "fft",
                    "frame_index": frame_idx, "sample_or_bin_index": bin_idx, "timestamp": ts, 
                    "ch0_adc_centered": "", "ch1_adc_centered": "",
                    "frequency_hz": round(target_f, 3), "fft_magnitude": round(nearest_mag, 6), "fs_actual": ""
                })

        fft_out = pd.DataFrame(fft_rows)

        time_csv_path = os.path.join(OUTPUT_DIR, f"raw_{new_device}_{new_mode}_time_{run_id_scaled}.csv")
        fft_csv_path = os.path.join(OUTPUT_DIR, f"raw_{new_device}_{new_mode}_fft_{run_id_scaled}.csv")
        time_out.to_csv(time_csv_path, index=False)
        fft_out.to_csv(fft_csv_path, index=False)
    
    return True

def main():
    print(f"🔍 소스 데이터 스캔 중: {RAW_DIR}")
    if not os.path.exists(RAW_DIR):
        print(f"❌ 경로가 존재하지 않습니다: {RAW_DIR}")
        return

    all_time_files = glob.glob(os.path.join(RAW_DIR, "raw_*_time_*.csv"))
    files_by_device = {}
    
    for path in all_time_files:
        try:
            df_head = pd.read_csv(path, nrows=1)
            dev = str(df_head["device"].iloc[0]).lower()
            if "synth_" in path or "_" in dev: continue
            if dev not in files_by_device: files_by_device[dev] = []
            files_by_device[dev].append(path)
        except Exception: pass

    devices = list(files_by_device.keys())
    print(f"✅ 발견된 단일 기기: {devices}")
    if len(devices) < 2: 
        print("⚠️ 합성을 위해 최소 2개 이상의 단일 기기 데이터가 필요합니다.")
        return

    device_pairs = list(itertools.combinations(devices, 2))
    all_combinations = []
    for dev_a, dev_b in device_pairs:
        combos = list(itertools.product(files_by_device[dev_a], files_by_device[dev_b]))
        all_combinations.extend(combos)

    total_combos = len(all_combinations)
    print(f"🚀 총 {total_combos}개의 조합 생성을 시작합니다.")
    
    success_count = 0
    for idx, (path_a, path_b) in enumerate(all_combinations, 1):
        if mix_and_save(path_a, path_b, idx, total_combos): success_count += 1

    print(f"\n🎉 작업 완료! (성공: {success_count}/{total_combos} 조합, 결과물은 {OUTPUT_DIR}에 저장됨)")

if __name__ == "__main__":
    main()