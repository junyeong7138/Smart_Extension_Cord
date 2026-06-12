#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
socket_timer.py
===============
소켓별 ON/OFF 예약 타이머 (핸드폰 알람처럼 설정 시각에 릴레이를 자동 ON/OFF).

- set_timer(sk, action, seconds): 소켓 sk 를 seconds 후에 action("on"/"off") 으로.
- cancel_timer(sk): 예약 취소.
- get_timers(): {sk: {"action","remaining","duration"}} — UI 카운트다운 표시용.

백그라운드 thread 가 주기적으로 만기된 타이머를 찾아 relay 동작을 실행하고,
orchestrator.on_external_relay_change(sk) 로 socket_state 를 동기화한다 (모바일 수동
토글과 동일 경로 → ON 이면 PENDING, OFF 면 DEVICE_OFF 전이).

기존 코드(분류/orchestrator/UI)는 건드리지 않는 *독립 모듈*. main.py 에서 생성·주입.
"""

import time
import threading
import logging


class TimerManager:
    def __init__(self, relay, orchestrator=None, poll_interval=0.5):
        self.relay = relay
        self.orchestrator = orchestrator
        self.poll_interval = poll_interval
        # sk -> {"action": "on"/"off", "fire_at": ts, "set_at": ts, "duration": int}
        self._timers = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None

    # -----------------------------------------------------------------
    # 공개 API
    # -----------------------------------------------------------------
    def set_timer(self, sk, action, seconds):
        """소켓 sk 에 seconds 후 action("on"/"off") 예약. seconds<=0 이면 예약 취소로 간주."""
        sk = int(sk)
        action = "on" if str(action).lower() in ("on", "1", "true") else "off"
        seconds = int(seconds)
        if seconds <= 0:
            self.cancel_timer(sk)
            return False
        now = time.time()
        with self._lock:
            self._timers[sk] = {
                "action": action,
                "fire_at": now + seconds,
                "set_at": now,
                "duration": seconds,
            }
        logging.info(
            f"[TIMER] socket{sk} {action.upper()} 예약: {seconds}s 후 "
            f"({self._fmt(seconds)})"
        )
        return True

    def cancel_timer(self, sk):
        sk = int(sk)
        with self._lock:
            existed = self._timers.pop(sk, None)
        if existed:
            logging.info(f"[TIMER] socket{sk} 예약 취소")
        return existed is not None

    def get_timers(self):
        """{sk: {"action","remaining","duration"}} — 남은 초(remaining)는 음수 방지 0 하한."""
        now = time.time()
        out = {}
        with self._lock:
            for sk, t in self._timers.items():
                remaining = int(round(t["fire_at"] - now))
                out[sk] = {
                    "action": t["action"],
                    "remaining": max(0, remaining),
                    "duration": t["duration"],
                }
        return out

    # -----------------------------------------------------------------
    # 백그라운드 실행
    # -----------------------------------------------------------------
    def start(self):
        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="socket_timer"
        )
        self._thread.start()
        logging.info("[TIMER] manager started")

    def close(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        logging.info("[TIMER] manager closed")

    def _loop(self):
        while not self._stop.is_set():
            try:
                self._check_fire()
            except Exception as e:  # noqa: BLE001
                logging.error(f"[TIMER] loop error: {e}")
            time.sleep(self.poll_interval)

    def _check_fire(self):
        now = time.time()
        due = []
        with self._lock:
            for sk, t in list(self._timers.items()):
                if now >= t["fire_at"]:
                    due.append((sk, t["action"]))
                    del self._timers[sk]
        for sk, action in due:
            self._fire(sk, action)

    def _fire(self, sk, action):
        on = (action == "on")
        try:
            self.relay.set(sk, on)
            if self.orchestrator is not None:
                try:
                    self.orchestrator.on_external_relay_change(sk)
                except Exception as e:  # noqa: BLE001
                    logging.warning(f"[TIMER] orchestrator sync 실패 socket{sk}: {e}")
            logging.info(f"[TIMER] socket{sk} 발화 → relay {action.upper()}")
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[TIMER] socket{sk} 발화 실패: {e}")

    @staticmethod
    def _fmt(sec):
        sec = max(0, int(sec))
        return f"{sec // 3600:02d}:{(sec % 3600) // 60:02d}:{sec % 60:02d}"


# =====================================================================
# 단독 self-test (Mock relay 로 1초 타이머 발화 확인)
# =====================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")

    class MockRelay:
        def __init__(self):
            self.st = {1: False, 2: False, 3: False, 4: False}

        def set(self, idx, on):
            self.st[idx] = on
            print(f"  [MOCK RELAY] socket{idx} -> {'ON' if on else 'OFF'}")

    r = MockRelay()
    tm = TimerManager(r, orchestrator=None, poll_interval=0.2)
    tm.start()

    print("=== socket2 ON 타이머 1초 예약 ===")
    tm.set_timer(2, "on", 1)
    print("  get_timers:", tm.get_timers())
    time.sleep(0.5)
    print("  0.5s 후 remaining:", tm.get_timers().get(2, {}).get("remaining"))
    time.sleep(0.8)
    print("  1.3s 후 relay2 =", r.st[2], "(True 기대), timers:", tm.get_timers())
    assert r.st[2] is True, "타이머 발화 실패!"

    print("\n=== socket3 OFF 타이머 예약 후 취소 ===")
    r.st[3] = True
    tm.set_timer(3, "off", 2)
    tm.cancel_timer(3)
    time.sleep(0.5)
    print("  취소 후 relay3 =", r.st[3], "(True 유지 기대), timers:", tm.get_timers())
    assert r.st[3] is True, "취소 실패 (발화돼버림)!"

    tm.close()
    print("\n✅ TimerManager self-test PASS")
