#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py
=======
NILM Multi-tap 시연 진입 코드 (v3 + touch/orchestrator 통합).

추가된 흐름
-----------
- TouchSensor: 터치 눌림 감지 → SocketOrchestrator.on_touch() 호출
- SocketOrchestrator: 물리 4 소켓의 *실제* 매핑을 관리. AIEngine 의 active_devices
  변화를 polling 으로 감지하고, 새 device 가 분류되면 릴레이 토글로 어느 물리 소켓인지
  식별. Device OFF 시 그 소켓 릴레이 OFF (대기전력 차단).
- 기존 AIEngine 의 기기 분류 로직은 손대지 않음. AIEngine 의 내부 socket 매핑은 그대로
  돌지만, 사용자에게 *유의미한* 매핑은 SocketOrchestrator 가 제공한다.
"""

import sys
import os
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NILM_DIR = os.path.join(BASE_DIR, "NILM")
sys.path.append(NILM_DIR)

from spi_core import SPICore
# 분류 엔진: ai_extension_v3 의 AIEngine 사용. UI 는 socket_dashboard 가 담당
# (ai_extension_v3.AIDashboardUI 는 가상 socket 을 그렸기 때문에 사용하지 않음).
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

    spi = SPICore()
    relay = RelayController()

    # 안전 상태로 출발 — 모든 릴레이 OFF
    relay.all_off()

    # AIEngine: 기기 분류만 담당. 내부 socket 매핑은 그대로 유지.
    engine = AIEngine(spi_core=spi)

    # SocketOrchestrator: 물리 소켓 매핑 + 토글 식별
    orchestrator = SocketOrchestrator(relay_controller=relay, ai_engine=engine)

    # TouchSensor: 누르면 orchestrator 에 알림
    touch = TouchSensor(on_press=orchestrator.on_touch)

    # mobile_ui: 실시간 전력 + 소켓별 기기 정보 표시 (engine, orchestrator 주입).
    # 수동 토글 백업 기능은 그대로 유지.
    mobile_ui.start_in_background(relay, engine=engine, orchestrator=orchestrator)

    # 백그라운드 시작
    orchestrator.start()
    touch.start()

    try:
        # 분류 엔진(engine) + 물리 매핑(orchestrator) 을 UI 에 주입.
        # UI 의 socket 표시는 engine 의 가상 socket 이 아니라 orchestrator 매핑을 따른다.
        dashboard = SocketDashboard(engine=engine, orchestrator=orchestrator)

        print("=" * 60)
        print(" WattsUp NILM Monitor")
        print(" - 분류: ai_extension_v3.AIEngine")
        print(" - 물리 socket 매핑: socket_orchestrator.SocketOrchestrator")
        print(" - UI: socket_dashboard.SocketDashboard")
        print(" - 터치센서: 빈 소켓 일괄 ON → 토글로 물리 위치 식별")
        print("=" * 60)

        dashboard.start()

    except KeyboardInterrupt:
        print("\nUser terminated.")
    finally:
        try:
            touch.close()
        except Exception as e:  # noqa: BLE001
            print(f"touch close error: {e}")
        try:
            orchestrator.close()
        except Exception as e:  # noqa: BLE001
            print(f"orchestrator close error: {e}")
        try:
            relay.close()
        except Exception as e:  # noqa: BLE001
            print(f"relay close error: {e}")
        try:
            spi.close()
        except Exception as e:  # noqa: BLE001
            print(f"spi close error: {e}")
        print("All resources closed safely.")


if __name__ == "__main__":
    main()
