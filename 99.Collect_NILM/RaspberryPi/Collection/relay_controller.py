#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
relay_controller.py
===================
자체 제작 4구 멀티탭의 SDA1_215R 릴레이 모듈 4채널을 Raspberry Pi GPIO 로 ON/OFF
제어한다. 각 릴레이는 L 상 전선에 연결되어 있고 (N 상은 공통), 채널 1~4 가
멀티탭 소켓 1~4 에 대응한다.

RPi.GPIO 미설치 환경(Mac 등) 에서는 Mock 으로 fallback. import 자체는 통과하므로
NILM 추론 흐름은 그대로 돌아간다 (시연 시 GPIO 가 동작 안 할 뿐).

[설정 - 실제 결선에 맞게 수정]
- RELAY_PINS  : 소켓 번호 → BCM GPIO 핀
- ACTIVE_HIGH : 릴레이가 ON 되는 GPIO 출력 레벨 (True = HIGH=ON / False = LOW=ON)
"""

import logging

# =========================================================================
# 결선 설정 (필요 시 수정)
# =========================================================================

# 소켓 번호 → BCM GPIO 핀 번호. 실제 결선에 맞게 변경.
RELAY_PINS = {
    1: 17,
    2: 27,
    3: 22,
    4: 23,
}

# True 면 GPIO HIGH = 릴레이 ON (사용자 확인됨).
ACTIVE_HIGH = True


# =========================================================================
# GPIO 백엔드 (Mock fallback)
# =========================================================================

class _MockGPIO:
    """RPi.GPIO 없는 환경(Mac) 에서 import 통과용. 동작은 로그만."""
    BCM = "BCM"
    OUT = "OUT"
    HIGH = 1
    LOW = 0

    def setmode(self, _m): pass
    def setwarnings(self, _b): pass

    def setup(self, pin, _mode, initial=None):
        logging.info(f"[MOCK GPIO] setup pin={pin} initial={initial}")

    def output(self, pin, val):
        logging.info(f"[MOCK GPIO] output pin={pin} val={val}")

    def cleanup(self, pins=None):
        logging.info(f"[MOCK GPIO] cleanup {pins}")


try:
    import RPi.GPIO as GPIO  # type: ignore
    _IS_REAL_GPIO = True
except ImportError:
    GPIO = _MockGPIO()
    _IS_REAL_GPIO = False
    logging.warning(
        "[RELAY] RPi.GPIO 미설치 → Mock 모드. Mac 등 개발 환경에서는 정상."
    )


# =========================================================================
# RelayController
# =========================================================================

class RelayController:
    """4채널 릴레이 컨트롤러.

    Usage:
        relay = RelayController()
        relay.set(1, True)         # 소켓1 ON
        relay.toggle(2)            # 소켓2 토글
        state = relay.get_state()  # {1: True, 2: False, 3: False, 4: False}
        relay.close()              # 종료 시 모두 OFF + GPIO cleanup
    """

    def __init__(self, pins=None, active_high=None):
        self.pins = dict(pins or RELAY_PINS)
        self.active_high = ACTIVE_HIGH if active_high is None else active_high
        self.is_real = _IS_REAL_GPIO
        self.state = {idx: False for idx in self.pins}

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in self.pins.values():
            # 부팅 직후 의도치 않은 ON 방지 → OFF 레벨로 초기화.
            off_level = GPIO.LOW if self.active_high else GPIO.HIGH
            GPIO.setup(pin, GPIO.OUT, initial=off_level)

        logging.info(
            f"[RELAY] init pins={self.pins} active_high={self.active_high} "
            f"real_gpio={self.is_real}"
        )

    # ------------------------------------------------------------------
    def _level_for(self, on: bool) -> int:
        if self.active_high:
            return GPIO.HIGH if on else GPIO.LOW
        return GPIO.LOW if on else GPIO.HIGH

    def set(self, idx: int, on: bool) -> bool:
        if idx not in self.pins:
            raise ValueError(f"unknown socket idx={idx} (valid={list(self.pins)})")
        pin = self.pins[idx]
        GPIO.output(pin, self._level_for(on))
        self.state[idx] = bool(on)
        logging.info(f"[RELAY] socket{idx} pin={pin} -> {'ON' if on else 'OFF'}")
        return self.state[idx]

    def toggle(self, idx: int) -> bool:
        return self.set(idx, not self.state.get(idx, False))

    def all_off(self):
        for idx in self.pins:
            self.set(idx, False)

    def get_state(self) -> dict:
        return dict(self.state)

    def close(self):
        try:
            self.all_off()
            GPIO.cleanup(list(self.pins.values()))
            logging.info("[RELAY] closed (all OFF, GPIO cleanup)")
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[RELAY] cleanup error: {e}")


# =========================================================================
# CLI 자가 테스트
# =========================================================================

if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    r = RelayController()
    print("Self-test: 각 소켓 1초씩 ON → OFF")
    try:
        for idx in r.pins:
            r.set(idx, True)
            time.sleep(5.0)
            r.set(idx, False)
            time.sleep(0.3)
    finally:
        r.close()
