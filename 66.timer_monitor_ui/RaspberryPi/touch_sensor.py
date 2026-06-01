#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
touch_sensor.py
===============
정전식/저항식 터치센서 입력을 polling 으로 받아 콜백을 호출한다.

- 누르면 (rising edge) on_press 콜백 호출
- 디바운스 (기본 200ms) 적용
- RPi.GPIO 미설치 환경(Mac 등) 에서는 Mock 모드 — 입력 없음으로 동작 (NILM 메인 흐름 영향 X)

[설정]
- TOUCH_PIN: BCM GPIO 핀 번호. 실제 결선에 맞게 변경.
- TOUCH_ACTIVE_HIGH: True 면 GPIO HIGH = 눌림. False 면 LOW = 눌림.
"""

import logging
import threading
import time

try:
    import RPi.GPIO as GPIO  # type: ignore
    _IS_REAL_GPIO = True
except ImportError:
    GPIO = None
    _IS_REAL_GPIO = False


# =====================================================================
# 설정 (결선에 맞게 수정)
# =====================================================================
TOUCH_PIN = 26          # BCM 핀 번호
TOUCH_ACTIVE_HIGH = True
DEBOUNCE_MS = 200
POLL_INTERVAL_S = 0.02  # 50Hz polling


class TouchSensor:
    """터치센서 polling 처리.

    Usage:
        ts = TouchSensor(on_press=callback)
        ts.start()
        ...
        ts.close()
    """

    def __init__(self, pin=TOUCH_PIN, active_high=TOUCH_ACTIVE_HIGH,
                 debounce_ms=DEBOUNCE_MS, on_press=None):
        self.pin = pin
        self.active_high = active_high
        self.debounce_s = debounce_ms / 1000.0
        self.on_press = on_press
        self.is_real = _IS_REAL_GPIO

        self._stop = threading.Event()
        self._thread = None
        self._last_press_time = 0.0

        if self.is_real:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                pull = GPIO.PUD_DOWN if active_high else GPIO.PUD_UP
                GPIO.setup(self.pin, GPIO.IN, pull_up_down=pull)
                logging.info(
                    f"[TOUCH] init pin={self.pin} active_high={self.active_high} real_gpio=True"
                )
            except Exception as e:
                logging.warning(f"[TOUCH] GPIO setup failed: {e} → Mock 모드로 fallback")
                self.is_real = False
        if not self.is_real:
            logging.info("[TOUCH] Mock 모드 (RPi.GPIO 미설치 또는 setup 실패). 입력 없음.")

    # ------------------------------------------------------------------
    def _read_pressed(self) -> bool:
        if not self.is_real:
            return False
        try:
            level = GPIO.input(self.pin)
            return level == GPIO.HIGH if self.active_high else level == GPIO.LOW
        except Exception:
            return False

    def _poll_loop(self):
        prev_pressed = False
        while not self._stop.is_set():
            pressed = self._read_pressed()
            if pressed and not prev_pressed:
                now = time.time()
                if now - self._last_press_time >= self.debounce_s:
                    self._last_press_time = now
                    logging.info("[TOUCH] press detected")
                    if self.on_press is not None:
                        try:
                            self.on_press()
                        except Exception as e:  # noqa: BLE001
                            logging.error(f"[TOUCH] on_press callback error: {e}")
            prev_pressed = pressed
            time.sleep(POLL_INTERVAL_S)

    # ------------------------------------------------------------------
    def start(self):
        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="touch_sensor"
        )
        self._thread.start()
        logging.info("[TOUCH] polling started")

    def close(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        if self.is_real:
            try:
                GPIO.cleanup(self.pin)
            except Exception:  # noqa: BLE001
                pass
        logging.info("[TOUCH] closed")


# =====================================================================
# CLI 자가 테스트
# =====================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    count = {"n": 0}

    def _on_press():
        count["n"] += 1
        print(f"=== TOUCH! 누른 횟수: {count['n']} ===")

    ts = TouchSensor(on_press=_on_press)
    ts.start()
    print("터치센서 자가 테스트. Ctrl+C 종료.")
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        ts.close()
