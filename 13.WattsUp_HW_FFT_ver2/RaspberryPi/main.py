from spi_core import SPICore
from dsp_engine import DSPEngine
from dashboard_ui import DashboardUI

def main():
    # 1. 시스템 컴포넌트 초기화 및 조립
    spi = SPICore()
    try:
        engine = DSPEngine(spi_core=spi)
        dashboard = DashboardUI(dsp_engine=engine) 
        
        # 2. 대시보드 구동 (여기서 무한 루프 실행)
        print("🚀 WattsUp DSP Monitor를 시작합니다...")
        dashboard.start()
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 시스템을 종료합니다.")
    finally:
        # 3. 종료 시 포트 안전 반환
        spi.close()
        print("SPI 포트가 안전하게 닫혔습니다.")

if __name__ == "__main__":
    main()