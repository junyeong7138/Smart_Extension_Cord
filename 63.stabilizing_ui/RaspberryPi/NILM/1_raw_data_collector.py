#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import csv
import time
import datetime
import numpy as np

# =========================================================
# 1. 기본 설정
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 💡 핵심: spi_core.py가 있는 상위 폴더(RaspberryPi)를 탐색 경로에 추가
PARENT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.append(PARENT_DIR)

# 이제 상위 폴더에 있는 모듈을 문제없이 불러올 수 있습니다!
from spi_core import SPICore
from dsp_engine import DSPEngine
from relay_controller import RelayController  # 수집 중 4채널 모두 ON 유지

RUN_ID = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

BUFFER_SIZE = 150

# FFT bin 주파수축: 30Hz ~ 480Hz (16개 bin)
# FPGA FFT 기준 bin으로 사용
FFT_FREQS_HZ = np.arange(1, 17) * 30.0

# CSV flush 주기
FLUSH_INTERVAL = 10

# FFT 프레임 저장 간격
# Time raw 150샘플 / 약 1920Hz ≈ 0.078초와 비슷하게 맞춤
FFT_FRAME_INTERVAL_SEC = 0.08

# =========================================================
# 2. 입력 함수
# =========================================================

# 💡 [추가된 부분] 기기 개수를 물어보는 함수
def ask_device_count():
    while True:
        ans = input("수집할 기기가 총 몇 개입니까? (1, 2, 3, 4): ").strip()
        if ans in ['1', '2', '3', '4']:
            return int(ans)
        print("⚠️ 1, 2, 3, 4 중에서 정확한 숫자를 입력해 주세요.")

def sanitize_name(text: str) -> str:
    text = text.strip()
    for ch in ['/', '\\', ' ', ':', '*', '?', '"', '<', '>', '|']:
        text = text.replace(ch, '_')
    return text


def ask_device_name() -> str:
    while True:
        name = input("디바이스명 입력: ").strip()
        if name:
            return sanitize_name(name.lower())
        print("디바이스명을 비워둘 수 없습니다.")


def ask_mode_name() -> str:
    while True:
        mode = input("디바이스 모드 입력: ").strip()
        if mode:
            return sanitize_name(mode.upper())
        print("디바이스 모드를 비워둘 수 없습니다.")


def ask_record_type() -> str:
    while True:
        print("\n수집 종류 선택")
        print("1. 전압/전류 RAW 수집")
        print("2. FPGA FFT RAW 수집")
        sel = input("선택 (1 / 2): ").strip()

        if sel == "1":
            return "time"
        if sel == "2":
            return "fft"

        print("1 또는 2만 입력하세요.")


# =========================================================
# 3. CSV 헤더
# =========================================================

CSV_HEADERS = [
    "run_id",
    "device",
    "mode",
    "record_type",
    "frame_index",
    "sample_or_bin_index",
    "timestamp",
    "ch0_adc_centered",
    "ch1_adc_centered",
    "frequency_hz",
    "fft_magnitude",
    "fs_actual",
]

# =========================================================
# 4. 수집 함수
# =========================================================

def collect_time_raw(
    engine: DSPEngine,
    writer: csv.writer,
    run_id: str,
    device: str,
    mode: str,
    csv_file
):
    print("\n[시작] 전압/전류 RAW 수집")
    print("Ctrl+C 로 종료")

    frame_index = 0
    pending_flush = 0

    while True:
        ch0_data, ch1_data, timestamps, fs_actual = engine.process_raw_mode()

        ch0_data = np.asarray(ch0_data)
        ch1_data = np.asarray(ch1_data)

        vrms_adc = float(np.sqrt(np.mean(ch0_data ** 2)))
        irms_adc = float(np.sqrt(np.mean(ch1_data ** 2)))

        for idx, (ts, ch0, ch1) in enumerate(zip(timestamps, ch0_data, ch1_data)):
            writer.writerow([
                run_id,
                device,
                mode,
                "time",
                frame_index,
                idx,
                round(float(ts), 6),
                int(ch0),
                int(ch1),
                "",
                "",
                round(float(fs_actual), 2),
            ])

        pending_flush += 1
        if pending_flush >= FLUSH_INTERVAL:
            csv_file.flush()
            pending_flush = 0

        frame_index += 1

        print(
            f"[frame {frame_index:5d}] "
            f"type=time | "
            f"samples={len(ch0_data)} | "
            f"Vrms_adc={vrms_adc:.2f} | "
            f"Irms_adc={irms_adc:.2f} | "
            f"fs={fs_actual:.1f}Hz"
        )


def collect_fft_raw(
    engine: DSPEngine,
    writer: csv.writer,
    run_id: str,
    device: str,
    mode: str,
    csv_file
):
    print("\n[시작] FPGA FFT RAW 수집")
    print("Ctrl+C 로 종료")

    frame_index = 0
    pending_flush = 0

    while True:
        ts = time.time()
        fft_y = engine.process_fft_mode()

        fft_y = np.asarray(fft_y)

        for idx, (freq, mag) in enumerate(zip(FFT_FREQS_HZ, fft_y)):
            writer.writerow([
                run_id,
                device,
                mode,
                "fft",
                frame_index,
                idx,
                round(float(ts), 6),
                "",
                "",
                round(float(freq), 3),
                round(float(mag), 6),
                "",
            ])

        pending_flush += 1
        if pending_flush >= FLUSH_INTERVAL:
            csv_file.flush()
            pending_flush = 0

        frame_index += 1

        if len(fft_y) > 0:
            peak_idx = int(np.argmax(fft_y))
            peak_freq = float(FFT_FREQS_HZ[peak_idx])
            peak_mag = float(fft_y[peak_idx])

            # 60Hz, 180Hz, 300Hz, 420Hz 확인용
            h1 = fft_y[1] if len(fft_y) > 1 else 0.0    # 60Hz
            h3 = fft_y[5] if len(fft_y) > 5 else 0.0    # 180Hz
            h5 = fft_y[9] if len(fft_y) > 9 else 0.0    # 300Hz
            h7 = fft_y[13] if len(fft_y) > 13 else 0.0  # 420Hz

            print(
                f"[frame {frame_index:5d}] "
                f"type=fft | "
                f"bins={len(fft_y)} | "
                f"peak_freq={peak_freq:.1f}Hz | "
                f"peak_mag={peak_mag:.2f} | "
                f"H1_60={h1:.1f} | "
                f"H3_180={h3:.1f} | "
                f"H5_300={h5:.1f} | "
                f"H7_420={h7:.1f}"
            )
        else:
            print(f"[frame {frame_index:5d}] type=fft | bins=0")

        time.sleep(FFT_FRAME_INTERVAL_SEC)


# =========================================================
# 5. 메인
# =========================================================

def main():
    # 💡 [수정된 부분] 기기 개수를 먼저 물어봅니다.
    device_count = ask_device_count()
    device = ask_device_name()
    mode = ask_mode_name()
    record_type = ask_record_type()

    # 💡 [수정된 부분] 입력받은 숫자에 따라 폴더명을 매핑합니다.
    folder_map = {1: "once", 2: "twice", 3: "thrice", 4: "quad"}
    sub_folder = folder_map[device_count]

    # 📂 새로운 통합 Data 폴더 경로 지정 (../../../00.Docs/Data/once 등)
    DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", "00.Docs", "Data", sub_folder))
    os.makedirs(DATA_DIR, exist_ok=True)

    # csv_path를 새로운 DATA_DIR 경로로 연결
    csv_path = os.path.join(
        DATA_DIR,
        f"raw_{device}_{mode}_{record_type}_{RUN_ID}.csv"
    )

    print("\n=== RAW 데이터 수집 시작 ===")
    print("RUN_ID   :", RUN_ID)
    print("COUNT    :", f"{device_count}개 ({sub_folder} 폴더에 저장)")
    print("DEVICE   :", device)
    print("MODE     :", mode)
    print("TYPE     :", record_type)
    print("CSV FILE :", csv_path)

    spi = None
    engine = None
    csv_file = None
    relay = None

    try:
        # 수집 환경과 시연 환경의 idle baseline 일치를 위해 4채널 릴레이 모두 ON 으로 고정.
        # (빈 소켓이어도 ON 상태에서 측정해야 시연 시 baseline 과 동일.)
        relay = RelayController()
        for sk_idx in (1, 2, 3, 4):
            relay.set(sk_idx, True)
        print("[RELAY] 4채널 모두 ON 으로 고정 (수집 환경 = 시연 환경 매칭)")

        spi = SPICore()
        engine = DSPEngine(spi_core=spi, buffer_size=BUFFER_SIZE)

        csv_file = open(csv_path, "w", newline="")
        writer = csv.writer(csv_file)
        writer.writerow(CSV_HEADERS)
        csv_file.flush()

        if record_type == "time":
            collect_time_raw(engine, writer, RUN_ID, device, mode, csv_file)
        elif record_type == "fft":
            collect_fft_raw(engine, writer, RUN_ID, device, mode, csv_file)
        else:
            raise RuntimeError(f"지원하지 않는 record_type: {record_type}")

    except KeyboardInterrupt:
        print("\n[종료] RAW 저장 완료")

    finally:
        if csv_file is not None:
            csv_file.close()
        if spi is not None:
            spi.close()
        if relay is not None:
            # RelayController.close() 는 all_off + GPIO cleanup 수행 (안전 종료).
            relay.close()


if __name__ == "__main__":
    main()