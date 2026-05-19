#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import importlib
from datetime import datetime

# =========================================================
# 0. Shell log 자동 저장 설정
# =========================================================
# main.py가 있는 RaspberryPi 폴더의 README.md에 실행 로그를 덮어쓴다.
# Ctrl+C로 종료해도 지금까지 출력된 stdout/stderr 내용이 남는다.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
README_LOG_PATH = os.path.join(BASE_DIR, "README.md")


class TeeLogger:
    """터미널 출력과 README.md 파일 출력을 동시에 수행하는 간단한 tee logger."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            try:
                stream.write(data)
                stream.flush()
            except Exception:
                pass
        return len(data)

    def flush(self):
        for stream in self.streams:
            try:
                stream.flush()
            except Exception:
                pass


def install_readme_logger():
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    log_file = open(README_LOG_PATH, "w", encoding="utf-8", buffering=1)
    log_file.write("# WattsUp 실행 로그\n\n")
    log_file.write(f"- 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_file.write(f"- 저장 위치: `{README_LOG_PATH}`\n\n")
    log_file.write("```text\n")
    log_file.flush()

    sys.stdout = TeeLogger(original_stdout, log_file)
    sys.stderr = TeeLogger(original_stderr, log_file)
    return log_file, original_stdout, original_stderr


def close_readme_logger(log_file, original_stdout, original_stderr):
    try:
        print(f"\n[LOG] README.md 저장 완료: {README_LOG_PATH}")
    except Exception:
        pass

    try:
        log_file.write("\n```\n")
        log_file.write(f"\n- 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.flush()
    except Exception:
        pass

    sys.stdout = original_stdout
    sys.stderr = original_stderr

    try:
        log_file.close()
    except Exception:
        pass


# =========================================================
# 1. 경로 설정
# =========================================================

# 현재 main.py 위치:
# /home/wattsup/Project/kwon/RaspberryPi/main.py
# BASE_DIR는 위에서 이미 선언함.

# NILM 폴더 위치:
# /home/wattsup/Project/kwon/RaspberryPi/NILM
NILM_DIR = os.path.join(BASE_DIR, "NILM")

# NILM 폴더를 실행 시 import 경로에 추가
if NILM_DIR not in sys.path:
    sys.path.insert(0, NILM_DIR)


# =========================================================
# 2. 모듈 동적 import
# =========================================================
# Pylance가 from ai_extension import ... 를 못 찾는 문제를 피하기 위해
# 문자열 기반 importlib로 불러온다.

spi_core_module = importlib.import_module("spi_core")
ai_extension_module = importlib.import_module("ai_extension")

SPICore = spi_core_module.SPICore
AIEngine = ai_extension_module.AIEngine
AIDashboardUI = ai_extension_module.AIDashboardUI


# =========================================================
# 3. main
# =========================================================

def main():
    log_file, original_stdout, original_stderr = install_readme_logger()
    spi = SPICore()

    try:
        engine = AIEngine(spi_core=spi)
        dashboard = AIDashboardUI(dsp_engine=engine)

        print("🚀 WattsUp DSP Monitor + AI를 시작합니다...")
        dashboard.start()

    except KeyboardInterrupt:
        print("\n사용자에 의해 시스템을 종료합니다.")

    finally:
        try:
            spi.close()
            print("SPI 포트가 안전하게 닫혔습니다.")
        finally:
            close_readme_logger(log_file, original_stdout, original_stderr)


if __name__ == "__main__":
    main()
