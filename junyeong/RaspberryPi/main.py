#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 💡 핵심 수정: 현재 폴더(RaspberryPi) 하위의 'NILM' 폴더를 탐색 경로에 추가합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NILM_DIR = os.path.join(BASE_DIR, "NILM")
sys.path.append(NILM_DIR)

# 이제 NILM 폴더 안에 있는 파일들과 현재 폴더에 있는 파일들을 자유롭게 불러올 수 있습니다!
from spi_core import SPICore
#from ai_extension import AIEngine, AIDashboardUI 


# 기존 ai_extension.py 파일에서 AIDashboardUI는 그대로 가져오고, 
# AIEngine만 새 파일인 ai_extension_v2에서 가져옵니다.
from ai_extension_v2 import AIEngine, AIDashboardUI
#from ai_extension import AIDashboardUI

def main():
    # 1. 시스템 컴포넌트 초기화 및 조립
    spi = SPICore()
    try:
        # 일반 부품 대신 AI가 결합된 부품으로 갈아 끼웁니다.
        engine = AIEngine(spi_core=spi)
        dashboard = AIDashboardUI(dsp_engine=engine) 
        
        # 2. 대시보드 구동 (무한 루프)
        print("🚀 WattsUp DSP Monitor + AI를 시작합니다...")
        dashboard.start()
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 시스템을 종료합니다.")
    finally:
        # 3. 종료 시 포트 안전 반환
        spi.close()
        print("SPI 포트가 안전하게 닫혔습니다.")

if __name__ == "__main__":
    main()