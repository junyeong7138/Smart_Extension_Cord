#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audio_alerts.py
===============
모니터(Pi, HDMI 스피커) 측 *꺼짐 임박* 소리 알림. 모바일 UI 의 JS 알림과 동일 규칙.

규칙
----
1. 음성 "OO가 곧 꺼질 예정입니다" (sounds/voice_*.wav, Yuna TTS 사전 생성):
   종료까지 잔여 시간이 20%(VOICE_REMAIN_FRAC) 남은 시점에 *에피소드당 1회*.
   - limit(안전 자동차단): get_socket_status 의 safety_warning 플래그가 정확히
     그 시점(80% 경과 = 20% 잔여, orchestrator SAFETY_WARN_FRAC)이므로 그대로 사용.
   - OFF timer: remaining ≤ duration × VOICE_REMAIN_FRAC.
2. 삐빅 알람 (sounds/beep.wav): 꺼지기 BEEP_WINDOW_S(5초) 전부터 꺼질 때까지
   BEEP_PERIOD_S 간격 반복. 단 음성 재생 중에는 대기, 끝난 뒤부터 (요구사양).

대상은 **limit + OFF timer 만**. PENDING 30s 만료 / ON timer / 수동 토글 등은 무음.

재생 백엔드: aplay(Pi) → afplay(Mac 개발) → 둘 다 없으면 mock(로그만).
소리 파일이 없어도 (sounds/ 미복사) 경고 로그 후 조용히 무시 — 대시보드는 계속 동작.
"""

import logging
import os
import shutil
import subprocess
import time

VOICE_REMAIN_FRAC = 0.2   # 잔여 20% 시점에 음성 (limit 은 safety_warning 플래그와 동일 시점)
BEEP_WINDOW_S = 5.0       # 꺼지기 5초 전부터 삐빅
BEEP_PERIOD_S = 0.9       # 삐빅 반복 간격

SOUNDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")


def compute_alerts(sk_status, timers,
                   voice_frac=VOICE_REMAIN_FRAC, beep_window_s=BEEP_WINDOW_S):
    """소켓별 알림 상태 계산 → {sk: {device, remaining, voice, beep}}.

    sk_status = orchestrator.get_socket_status() (safety_warning/safety_remaining 사용),
    timers    = timer_manager.get_timers()       (action/remaining/duration 사용).
    limit 과 OFF timer 가 같은 소켓에 겹치면 OR 병합(remaining 은 더 급한 쪽).
    """
    alerts = {}
    for sk, s in (sk_status or {}).items():
        if s.get("safety_warning") and s.get("safety_remaining") is not None:
            rem = float(s["safety_remaining"])
            alerts[sk] = {
                "device": s.get("device"), "remaining": rem,
                "voice": True, "beep": rem <= beep_window_s,
            }
    for sk, t in (timers or {}).items():
        if t.get("action") != "off":
            continue                                   # ON timer 는 무음
        rem = float(t.get("remaining", 0) or 0)
        dur = float(t.get("duration", 0) or 0)
        voice = dur > 0 and rem <= dur * voice_frac
        beep = rem <= beep_window_s
        if not (voice or beep):
            continue
        dev = (sk_status or {}).get(sk, {}).get("device")
        cur = alerts.get(sk)
        if cur:
            cur["voice"] = cur["voice"] or voice
            cur["beep"] = cur["beep"] or beep
            cur["remaining"] = min(cur["remaining"], rem)
        else:
            alerts[sk] = {"device": dev, "remaining": rem, "voice": voice, "beep": beep}
    return alerts


class AudioAlerts:
    """소켓별 음성 1회 + 삐빅 반복 재생 상태머신. 매 UI frame update(alerts) 호출."""

    def __init__(self, sounds_dir=SOUNDS_DIR, player=None):
        self.sounds_dir = sounds_dir
        self.player = player if player is not None else self._detect_player()
        self.beep_path = os.path.join(sounds_dir, "beep.wav")
        self._voice_done = set()      # 이번 에피소드에 음성 끝낸 소켓
        self._voice_proc = None       # 재생 중인 음성 subprocess (삐빅 대기용)
        self._last_beep_t = 0.0
        if self.player is None:
            logging.warning("[AUDIO] aplay/afplay 없음 → mock 모드 (로그만)")
        else:
            logging.info(f"[AUDIO] player={self.player}, sounds={sounds_dir}")

    @staticmethod
    def _detect_player():
        for cand in ("aplay", "afplay"):   # Pi → Mac 개발 순
            if shutil.which(cand):
                return cand
        return None

    def _voice_path_for(self, device):
        p = os.path.join(self.sounds_dir, f"voice_{device}.wav") if device else None
        if p and os.path.exists(p):
            return p
        return os.path.join(self.sounds_dir, "voice_generic.wav")

    def _play(self, path):
        """비차단 재생. 반환: subprocess (mock/실패 시 None)."""
        if self.player is None:
            logging.info(f"[AUDIO] (mock) play {os.path.basename(path)}")
            return None
        if not os.path.exists(path):
            logging.warning(f"[AUDIO] 소리 파일 없음: {path} (sounds/ 복사 확인)")
            return None
        try:
            return subprocess.Popen(
                [self.player, path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[AUDIO] 재생 실패 ({path}): {e}")
            return None

    def _voice_playing(self):
        return self._voice_proc is not None and self._voice_proc.poll() is None

    def update(self, alerts):
        """alerts = compute_alerts(...) 결과. 매 frame(≈100ms) 호출해도 안전(중복 방지 내장)."""
        alerts = alerts or {}
        now = time.time()

        # 에피소드 리셋: 알림이 사라진 소켓(꺼짐 완료/타이머 취소/재가동)은 음성 1회 플래그 해제
        self._voice_done &= set(alerts.keys())

        # 1) 음성 — 소켓·에피소드당 1회
        for sk, a in alerts.items():
            if a.get("voice") and sk not in self._voice_done:
                self._voice_done.add(sk)
                proc = self._play(self._voice_path_for(a.get("device")))
                if proc is not None:
                    self._voice_proc = proc
                logging.info(
                    f"[AUDIO] voice: socket{sk} ({a.get('device') or 'generic'}), "
                    f"remaining={a.get('remaining')}"
                )

        # 2) 삐빅 — beep 소켓이 하나라도 있으면 반복. 음성 재생 중엔 대기(요구사양).
        if any(a.get("beep") for a in alerts.values()):
            if not self._voice_playing() and now - self._last_beep_t >= BEEP_PERIOD_S:
                self._last_beep_t = now
                self._play(self.beep_path)


# =====================================================================
# CLI 자가 테스트 (Mac: python RaspberryPi/ui/audio_alerts.py — mock player)
# =====================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    print("=== compute_alerts 규칙 검증 ===")
    # limit: safety_warning → voice, 5초 이하부터 beep
    st = {1: {"device": "dryer", "safety_warning": True, "safety_remaining": 6},
          2: {"device": "tv", "safety_warning": False, "safety_remaining": None}}
    a = compute_alerts(st, {})
    assert a[1]["voice"] and not a[1]["beep"] and 2 not in a
    a = compute_alerts({1: {"device": "dryer", "safety_warning": True,
                            "safety_remaining": 4}}, {})
    assert a[1]["beep"], "5초 이하인데 beep 아님!"

    # OFF timer: duration 30s → 잔여 6s(=20%)부터 voice, 5s부터 beep. ON timer 는 무음.
    a = compute_alerts({}, {3: {"action": "off", "remaining": 10, "duration": 30}})
    assert 3 not in a, "잔여 10s/30s 인데 알림 발생!"
    a = compute_alerts({}, {3: {"action": "off", "remaining": 6, "duration": 30}})
    assert a[3]["voice"] and not a[3]["beep"]
    a = compute_alerts({}, {3: {"action": "off", "remaining": 5, "duration": 30}})
    assert a[3]["voice"] and a[3]["beep"]
    a = compute_alerts({}, {3: {"action": "on", "remaining": 2, "duration": 30}})
    assert 3 not in a, "ON timer 인데 알림 발생!"
    print("  ✅ limit/OFF-timer/ON-timer 규칙 OK")

    print("=== AudioAlerts 상태머신 검증 (mock player) ===")
    played = []

    class TestAlerts(AudioAlerts):
        def _play(self, path):
            played.append(os.path.basename(path))
            return None

    aa = TestAlerts(player="mock")
    al = {1: {"device": "dryer", "remaining": 6, "voice": True, "beep": False}}
    aa.update(al); aa.update(al); aa.update(al)
    assert played == ["voice_dryer.wav"], f"음성 1회만 재생돼야 함: {played}"

    al[1]["beep"] = True; al[1]["remaining"] = 4
    aa.update(al)
    assert played == ["voice_dryer.wav", "beep.wav"], f"beep 시작 실패: {played}"
    aa.update(al)   # BEEP_PERIOD_S 안 지남 → 추가 beep 없어야
    assert played.count("beep.wav") == 1, "beep 간격 무시하고 연타!"
    aa._last_beep_t = 0
    aa.update(al)
    assert played.count("beep.wav") == 2, "주기 지난 beep 미재생!"

    aa.update({})                       # 꺼짐/해소 → 에피소드 리셋
    aa.update(al)                       # 새 에피소드 → 음성 다시 1회
    assert played.count("voice_dryer.wav") == 2, "에피소드 리셋 후 음성 재발화 실패!"

    # 라벨 없는 소켓 → generic
    aa.update({2: {"device": None, "remaining": 3, "voice": True, "beep": False}})
    assert "voice_generic.wav" in played

    print(f"  ✅ played sequence: {played}")
    print("\n✅ ALL PASS")
