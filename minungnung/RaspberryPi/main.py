#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
=======
WattsUp NILM Multi-tap 시연 진입 코드.

중요
----
- NILM 판단 로직(ai_extension_v3.py)은 수정하지 않는다.
- 물리 소켓 구분/릴레이 probe 로직(socket_orchestrator.py)은 수정하지 않는다.
- 모바일 UI는 relay / AIEngine / SocketOrchestrator 상태를 읽어서 표시만 한다.

실행 흐름
---------
1. SPICore 생성
2. RelayController 생성 및 모든 릴레이 OFF
3. AIEngine 생성
4. SocketOrchestrator 생성
5. TouchSensor 생성
6. mobile_ui 백그라운드 실행
7. orchestrator / touch 시작
8. SocketDashboard 시연 화면 시작
"""

import logging
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NILM_DIR = os.path.join(BASE_DIR, "NILM")
if NILM_DIR not in sys.path:
    sys.path.insert(0, NILM_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from spi_core import SPICore
from ai_extension_v3 import AIEngine
from socket_dashboard import SocketDashboard
from relay_controller import RelayController
from touch_sensor import TouchSensor
from socket_orchestrator import SocketOrchestrator
import mobile_ui


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    spi = None
    relay = None
    engine = None
    orchestrator = None
    touch = None

    try:
        spi = SPICore()
        relay = RelayController()

        # 안전 상태로 출발: 모든 릴레이 OFF
        relay.all_off()

        # AIEngine: NILM 기기 분류 담당. 내부 로직은 건드리지 않는다.
        engine = AIEngine(spi_core=spi)

        # SocketOrchestrator: 실제 물리 소켓 매핑 + 릴레이 토글 식별 담당.
        orchestrator = SocketOrchestrator(relay_controller=relay, ai_engine=engine)

        # TouchSensor: 터치 입력 시 기존과 동일하게 PENDING 활성화.
        touch = TouchSensor(on_press=orchestrator.on_touch)

        # 모바일 대시보드: NILM/소켓구분 로직을 수정하지 않고 상태만 읽어 표시.
        # 핵심: orchestrator를 반드시 넘겨야 모바일 UI에서 소켓별 기기 매핑을 정확히 볼 수 있다.
        mobile_ui.start_in_background(
            relay=relay,
            ai_engine=engine,
            orchestrator=orchestrator,
            port=5000,
        )

        # 백그라운드 시작
        orchestrator.start()
        touch.start()

        print("=" * 64)
        print(" WattsUp NILM Monitor")
        print(" - NILM 분류: ai_extension_v3.AIEngine")
        print(" - 물리 소켓 매핑: socket_orchestrator.SocketOrchestrator")
        print(" - PC 시연 화면: socket_dashboard.SocketDashboard")
        print(" - 모바일 화면: mobile_ui Flask Dashboard")
        print(" - 터치센서/PENDING/소켓 식별 로직은 기존 흐름 유지")
        print("=" * 64)

        # PC 시연 화면. SocketDashboard가 orchestrator 상태를 받아 소켓별 매핑을 표시한다.
        dashboard = SocketDashboard(engine=engine, orchestrator=orchestrator)
        dashboard.start()

    except KeyboardInterrupt:
        print("\nUser terminated.")
    finally:
        # 종료 시 안전하게 정리
        for name, obj, method in [
            ("touch", touch, "close"),
            ("orchestrator", orchestrator, "close"),
            ("relay", relay, "close"),
            ("spi", spi, "close"),
        ]:
            if obj is None:
                continue
            try:
                getattr(obj, method)()
            except Exception as e:  # noqa: BLE001
                print(f"{name} close error: {e}")
        print("All resources closed safely.")


if __name__ == "__main__":
    main()