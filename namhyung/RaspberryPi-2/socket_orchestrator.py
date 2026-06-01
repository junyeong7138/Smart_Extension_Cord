#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
socket_orchestrator.py
======================

WattsUp NILM 스마트 멀티탭용 물리 소켓 관리기.

핵심 역할
---------
- AIEngine은 전체 CT/PT 파형으로 "무슨 기기인지"와 ON/OFF 이벤트만 판단한다.
- SocketOrchestrator는 그 기기를 실제 1~4번 물리 소켓에 매핑하고 릴레이를 제어한다.

v85 안정화 방향
---------------
1. DEVICE_OFF 소켓 자동 정리
   - OFF 후 일정 시간 동안은 DEVICE_OFF로 남겨 재사용/복구가 가능하게 한다.
   - 시스템에 ASSIGNED 기기가 하나도 없고, OFF 후 시간이 충분히 지나면 EMPTY로 정리한다.
   - 이렇게 해야 "OFF 상태가 계속 남아서 다음 시연에 꼬이는 문제"를 줄일 수 있다.

2. 터치 노이즈 방지
   - ASSIGNED 상태의 기기가 하나라도 켜져 있을 때 들어오는 touch는 기본적으로 무시한다.
   - 이유: 실측 로그에서 microwave 동작 중 터치 노이즈가 들어와 socket1~3이 PENDING으로 바뀌고,
     microwave settling 신호가 charger_on으로 오인식되었다.
   - 이미 처음 터치로 빈 소켓 전체를 켜놓는 시연 방식에서는 동작 중 추가 touch가 필요 없다.
   - 동작 중 특정 소켓만 다시 켜야 할 때는 mobile UI의 개별 relay 제어를 사용한다.

3. PENDING 없는 ON 이벤트 rollback
   - AIEngine이 새 기기 ON을 감지했는데 물리적으로 대기 중인 PENDING 소켓이 없으면
     false ON으로 보고 AIEngine active_devices/signature를 정리한다.
   - 이게 없으면 "꽂지도 않았는데 charger_on" 같은 ghost active가 남는다.

4. OFF verify 유지
   - AIEngine이 "dev OFF"라고 판단하면, 해당 dev가 매핑된 물리 소켓을 짧게 OFF/ON해서
     실제 부하가 여전히 있는지 검증한다.
   - 변화가 크면 false OFF로 보고 reject, 변화가 작으면 진짜 OFF로 confirm한다.
   - raw Irms와 60Hz H1을 함께 측정해 전류량/주파수 성분 기반 보조 판단을 한다.

주의
----
- 전체 CT/PT 1개 구조에서는 여러 PENDING 소켓 중 실제 위치를 100% 자동 식별할 수 없다.
- 따라서 toggle-identify는 보조 수단이며, 실패 시 임의 fallback 배정을 하지 않는다.
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Tuple

import numpy as np


ORCH_VERSION = "socket_orchestrator_2026_05_31_v100_toggle_h5"

# =====================================================================
# 기본 설정
# =====================================================================
PHYSICAL_SOCKETS = [1, 2, 3, 4]

SOCKET_STATE_EMPTY = "EMPTY"             # 릴레이 OFF, 기기 없음
SOCKET_STATE_PENDING = "PENDING"         # 릴레이 ON, 새 기기 연결/식별 대기
SOCKET_STATE_ASSIGNED = "ASSIGNED"       # 기기 매핑 완료, 릴레이 ON
SOCKET_STATE_DEVICE_OFF = "DEVICE_OFF"   # OFF 확정, 릴레이 OFF, 최근 기기 라벨 보존

LOW_POWER_DEVICES = frozenset({"charger", "tv"})
HIGH_POWER_DEVICES = frozenset({"cleaner", "dryer", "microwave"})

# v91: 전체 CT/PT 1개 구조에서는 charger/tv 위치를 토글로 안정적으로 찾기 어렵다.
# 캡스톤 시연 안정성을 위해 bulk touch로 열린 PENDING에서는 저전력 기기의
# 물리 소켓을 장치별 기본 위치로 우선 배정한다.
# - charger는 1번
# - tv는 2번
# 이 정책이면 TV를 먼저 2번에 꽂고 charger를 나중에 1번에 꽂아도 뒤집히지 않는다.
# 단, mobile UI로 특정 소켓만 직접 ON/PENDING한 경우는 사용자의 명시적 선택으로 보고
# v97: LP_PREFERRED_SOCKET / USE_LP_PREFERRED_SOCKET_FOR_BULK 제거 (LP PENDING-순서 cheat).

# 터치 정책
# ASSIGNED 기기가 하나라도 켜진 동안 touch 일괄 재활성화를 막는다.
# 동작 중 소켓 하나를 일부러 켜려면 mobile UI 개별 relay ON을 사용한다.
BLOCK_TOUCH_WHILE_ANY_ASSIGNED = True

# DEVICE_OFF → EMPTY 자동 정리.
# 단, ASSIGNED 기기가 하나도 없을 때만 정리한다.
DEVICE_OFF_TO_EMPTY_S = 60.0

# OFF 직후 너무 빠른 재활성화 방지.
DEVICE_OFF_TO_PENDING_COOLDOWN_S = 10.0

# 오래 방치된 PENDING 자동 회수.
# 너무 짧으면 사용자가 꽂기 전에 꺼지므로 넉넉하게 둔다.
PENDING_TIMEOUT_S = 120.0

# AIEngine event cooldown mute
ENGINE_MUTE_FRAMES = 35

# monitor
MONITOR_INTERVAL_S = 0.20

# ON toggle-identify
TOGGLE_N_BEFORE = 4
TOGGLE_N_OFF = 6
TOGGLE_EXCLUDE_FIRST = 1
TOGGLE_N_RESTORE = 2
TOGGLE_MIN_PRESENCE_RATIO = 0.45
TOGGLE_MIN_ABS_I = 3.0
TOGGLE_MIN_ABS_H1 = 80.0
TOGGLE_AMBIG_RATIO = 0.80
# v86: mobile UI로 여러 소켓을 직접 PENDING 시킨 뒤 저전력 기기를 꽂는 경우,
# microwave/dryer 같은 active high-power 노이즈 때문에 1·2위 점수가 근접할 수 있다.
# 이때는 "가장 최근에 외부 UI로 arm 된 소켓"이 close 후보 안에 있으면 그 소켓을 채택한다.
# v97: TOGGLE_MANUAL_ARM_CLOSE_RATIO 제거 (toggle ambiguous MANUAL-ARM cheat).

# OFF verify
OFF_VERIFY_RELAY_GAP_S = 0.50
OFF_VERIFY_SETTLE_S = 0.05
OFF_VERIFY_MIN_SAMPLES = 4
OFF_VERIFY_RESIDUAL_RATIO_REJECT = 0.70
OFF_VERIFY_RESIDUAL_RATIO_CONFIRM = 0.30
OFF_VERIFY_NOISE_STD_LIMIT = 8.0
OFF_VERIFY_MIN_DELTA_I = 5.0
OFF_VERIFY_MIN_DELTA_H1 = 120.0
OFF_VERIFY_FALLBACK_RATIO_ABSENT = 0.30
# v92: HP active 중 LP(charger/tv) OFF VERIFY 구제용 상수.
# HP 대전류 노이즈가 작은 LP sig 를 가려, 그 소켓만 토글해도 ΔI/ΔH1 이 HP duty 노이즈에
# 지배된다. 살아있는 LP 는 sig 만큼 빠져 ratio≈1.0 (residual band [REJECT, OVERSHOOT]).
# 뽑힌 LP 는 ΔI/ΔH1 이 노이즈만 → ratio 가 band 밖 (REJECT 미만 = tv 0.5~0.6, 또는
# OVERSHOOT 초과 = charger 2~4). band 밖이면 absent confirm. HARD 초과는 라벨 오류성
# 대형 잔존 (HP 가 이 소켓에 매핑) → reject 유지.
OFF_VERIFY_RESIDUAL_RATIO_OVERSHOOT = 1.8
OFF_VERIFY_RESIDUAL_RATIO_HARD = 6.0


class SocketOrchestrator:
    """터치센서, AIEngine, RelayController 사이의 물리 소켓 상태 관리자."""

    def __init__(self, relay_controller, ai_engine, lock=None):
        self.relay = relay_controller
        self.engine = ai_engine
        self.lock = lock or threading.RLock()
        self.engine_lock = threading.RLock()

        self.socket_state: Dict[int, str] = {
            sk: SOCKET_STATE_EMPTY for sk in PHYSICAL_SOCKETS
        }
        self.socket_device: Dict[int, Optional[str]] = {
            sk: None for sk in PHYSICAL_SOCKETS
        }
        self.socket_device_sig: Dict[int, Optional[dict]] = {
            sk: None for sk in PHYSICAL_SOCKETS
        }
        self._socket_off_time: Dict[int, float] = {
            sk: 0.0 for sk in PHYSICAL_SOCKETS
        }
        self._socket_pending_time: Dict[int, float] = {
            sk: 0.0 for sk in PHYSICAL_SOCKETS
        }
        # v86: PENDING 전환 순서/출처 추적.
        # - touch bulk로 열린 PENDING은 자동 순서 추정에 쓰지 않는다.
        # - mobile UI 개별 ON으로 열린 PENDING은 사용자의 명시적 의도이므로,
        #   저전력 toggle-id가 애매할 때 가장 최근 외부 arm 소켓을 우선할 수 있다.
        self._pending_seq = 0
        self._socket_pending_seq: Dict[int, int] = {
            sk: 0 for sk in PHYSICAL_SOCKETS
        }
        self._socket_pending_source: Dict[int, str] = {
            sk: "" for sk in PHYSICAL_SOCKETS
        }

        self._prev_active = set()
        self._identifying = False
        self._stop = threading.Event()
        self._thread = None
        self.last_event = None

        # OFF verify reject 비율 기록. exhaust fallback에서 standby corruption 방지에 사용.
        self._off_verify_reject_ratios: Dict[str, float] = {}
        self._off_verify_last_callback_t = 0.0

        logging.info(f"[ORCH VERSION] {ORCH_VERSION}")

        try:
            self.relay.all_off()
            logging.info("[ORCH] init: all relays OFF (safe state)")
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[ORCH] init all_off failed: {e}")

        self._patch_engine_for_win_feat_capture()

        # AIEngine OFF 검증 hook 등록
        try:
            self.engine._off_verify_callback = self._off_verify_callback
            self.engine._off_verify_exhaust_fallback = self._off_verify_exhaust_fallback
            logging.info("[ORCH] OFF verify callback + exhaust fallback registered to AIEngine")
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[ORCH] OFF verify callback registration failed: {e}")

    # ==================================================================
    # Engine patch
    # ==================================================================
    def _patch_engine_for_win_feat_capture(self):
        original_process = self.engine.process_ai_frame
        engine_ref = self.engine

        def wrapped_process(*args, **kwargs):
            status = original_process(*args, **kwargs)
            try:
                if status is not None and "win_feat" in status:
                    engine_ref._latest_win_feat = status["win_feat"]
            except Exception:  # noqa: BLE001
                pass
            return status

        self.engine.process_ai_frame = wrapped_process
        logging.info("[ORCH] engine.process_ai_frame wrapped for win_feat capture")

    # ==================================================================
    # Touch / external relay
    # ==================================================================
    def on_touch(self):
        """터치센서 콜백.

        기본 UX는 유지한다.
        - 시스템이 idle이면 EMPTY/DEVICE_OFF 소켓 전체 relay ON → PENDING.
        - 단, 이미 ASSIGNED 기기가 동작 중이면 touch 노이즈로 보고 무시한다.
        """
        with self.lock:
            now = time.perf_counter()
            assigned = self._assigned_sockets_unlocked()
            if BLOCK_TOUCH_WHILE_ANY_ASSIGNED and assigned:
                self.last_event = (
                    f"touch ignored - active ASSIGNED sockets exist {assigned}; "
                    f"use mobile UI for single-socket rearm"
                )
                logging.info(f"[ORCH][TOUCH-GUARD v89] {self.last_event}")
                return []

            activated = []
            blocked = []
            for sk in PHYSICAL_SOCKETS:
                state = self.socket_state[sk]
                if state == SOCKET_STATE_EMPTY:
                    self._set_socket_pending_unlocked(sk, clear_label=True, source="touch_bulk")
                    activated.append(sk)
                elif state == SOCKET_STATE_DEVICE_OFF:
                    since_off = now - self._socket_off_time.get(sk, 0.0)
                    if since_off < DEVICE_OFF_TO_PENDING_COOLDOWN_S:
                        blocked.append((sk, since_off))
                        continue
                    self._set_socket_pending_unlocked(sk, clear_label=False, source="touch_bulk")
                    activated.append(sk)

            if activated:
                self.last_event = f"touch → sockets {activated} relay ON (PENDING, bulk)"
                logging.info(f"[ORCH] {self.last_event}")
            elif blocked:
                msg = ", ".join(f"S{s}({t:.1f}s)" for s, t in blocked)
                self.last_event = f"touch ignored - DEVICE_OFF cooldown: {msg}"
                logging.info(f"[ORCH] {self.last_event}")
            else:
                self.last_event = "touch ignored - no EMPTY/DEVICE_OFF socket"
                logging.info(f"[ORCH] {self.last_event} ({self._state_summary()})")
            return activated

    def on_external_relay_change(self, sk):
        """mobile UI 등 외부에서 relay를 직접 바꾼 뒤 호출되는 동기화 API.

        외부 개별 relay ON은 사용자의 명시적 의도라고 보고 active 기기가 있어도 허용한다.
        """
        if sk not in PHYSICAL_SOCKETS:
            return
        with self.lock:
            try:
                actual_on = bool(self.relay.get_state().get(sk, False))
            except Exception as e:  # noqa: BLE001
                logging.warning(f"[ORCH] external relay sync: relay state read failed: {e}")
                return

            cur = self.socket_state.get(sk)
            now = time.perf_counter()

            if actual_on:
                if cur in (SOCKET_STATE_EMPTY, SOCKET_STATE_DEVICE_OFF):
                    # DEVICE_OFF의 기존 라벨은 보존한다. 같은 기기 재사용/자동복원 판단에 도움.
                    self.socket_state[sk] = SOCKET_STATE_PENDING
                    self._socket_pending_time[sk] = now
                    self._pending_seq += 1
                    self._socket_pending_seq[sk] = self._pending_seq
                    self._socket_pending_source[sk] = "external"
                    logging.info(
                        f"[ORCH] external relay ON socket{sk}: {cur} → PENDING "
                        f"(preserved label={self.socket_device.get(sk)})"
                    )
                return

            # actual OFF
            if cur == SOCKET_STATE_ASSIGNED:
                dev = self.socket_device.get(sk)
                self._snapshot_socket_signature_unlocked(sk, dev)
                self.socket_state[sk] = SOCKET_STATE_DEVICE_OFF
                self._socket_off_time[sk] = now
                self._remove_engine_active_unlocked(dev, reason=f"external relay OFF socket{sk}")
                logging.info(f"[ORCH] external relay OFF socket{sk}: ASSIGNED({dev}) → DEVICE_OFF")
            elif cur == SOCKET_STATE_PENDING:
                if self.socket_device.get(sk):
                    self.socket_state[sk] = SOCKET_STATE_DEVICE_OFF
                    self._socket_off_time[sk] = now
                    logging.info(
                        f"[ORCH] external relay OFF socket{sk}: PENDING → DEVICE_OFF "
                        f"(label={self.socket_device.get(sk)} preserved)"
                    )
                else:
                    self.socket_state[sk] = SOCKET_STATE_EMPTY
                    self.socket_device[sk] = None
                    self.socket_device_sig[sk] = None
                    logging.info(f"[ORCH] external relay OFF socket{sk}: PENDING → EMPTY")

    def _set_socket_pending_unlocked(self, sk: int, clear_label: bool, source: str = "touch_bulk"):
        self.relay.set(sk, True)
        self.socket_state[sk] = SOCKET_STATE_PENDING
        self._socket_pending_time[sk] = time.perf_counter()
        self._pending_seq += 1
        self._socket_pending_seq[sk] = self._pending_seq
        self._socket_pending_source[sk] = source
        if clear_label:
            self.socket_device[sk] = None
            self.socket_device_sig[sk] = None

    # ==================================================================
    # Monitor loop
    # ==================================================================
    def start(self):
        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="socket_orch")
        self._thread.start()
        logging.info("[ORCH] monitor started")

    def close(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        logging.info("[ORCH] closed")

    def _monitor_loop(self):
        while not self._stop.is_set():
            try:
                if not self._identifying:
                    self._check_engine_changes()
            except Exception as e:  # noqa: BLE001
                logging.error(f"[ORCH] monitor error: {e}")
            time.sleep(MONITOR_INTERVAL_S)

    def _check_engine_changes(self):
        with self.lock:
            self._cleanup_pending_and_device_off_unlocked()

            current_active = set(self.engine.active_devices.keys())
            new_devices = current_active - self._prev_active
            removed_devices = self._prev_active - current_active

            # LP label swap 감지: charger↔tv 라벨만 바뀐 경우 socket 라벨도 따라 변경.
            removed_lp = removed_devices & LOW_POWER_DEVICES
            new_lp = new_devices & LOW_POWER_DEVICES
            if len(removed_lp) == 1 and len(new_lp) == 1:
                old_dev = next(iter(removed_lp))
                new_dev = next(iter(new_lp))
                old_sk = next((s for s, d in self.socket_device.items() if d == old_dev), None)
                new_sk_engine = self.engine.active_devices.get(new_dev)
                if old_sk is not None and (new_sk_engine is None or new_sk_engine == old_sk):
                    self.relabel_device(old_dev, new_dev)
                    removed_devices.discard(old_dev)
                    new_devices.discard(new_dev)

            for dev in removed_devices:
                self._handle_device_off(dev)

            for dev in new_devices:
                already_assigned = any(
                    self.socket_device.get(sk) == dev and self.socket_state.get(sk) == SOCKET_STATE_ASSIGNED
                    for sk in PHYSICAL_SOCKETS
                )
                if already_assigned:
                    continue
                self._identify_socket_for_device(dev)

            self._prev_active = set(self.engine.active_devices.keys())

    def _cleanup_pending_and_device_off_unlocked(self):
        now = time.perf_counter()
        has_assigned = bool(self._assigned_sockets_unlocked())

        # 오래된 PENDING 회수. relay도 OFF해서 ghost ON 트리거를 줄인다.
        for sk in PHYSICAL_SOCKETS:
            if self.socket_state[sk] == SOCKET_STATE_PENDING:
                age = now - self._socket_pending_time.get(sk, now)
                if age > PENDING_TIMEOUT_S:
                    try:
                        self.relay.set(sk, False)
                    except Exception:  # noqa: BLE001
                        pass
                    self.socket_state[sk] = SOCKET_STATE_EMPTY
                    self.socket_device[sk] = None
                    self.socket_device_sig[sk] = None
                    self._socket_pending_seq[sk] = 0
                    self._socket_pending_source[sk] = ""
                    logging.info(f"[ORCH][PENDING TIMEOUT v90] socket{sk} PENDING {age:.1f}s → EMPTY")

        # 모든 기기가 꺼진 완전 idle 상태에서만 DEVICE_OFF를 EMPTY로 정리.
        # active 기기가 남아 있는 동안에는 OFF 라벨을 보존해 잘못된 bulk touch 재활성화를 막는다.
        if not has_assigned:
            for sk in PHYSICAL_SOCKETS:
                if self.socket_state[sk] == SOCKET_STATE_DEVICE_OFF:
                    age = now - self._socket_off_time.get(sk, now)
                    if age >= DEVICE_OFF_TO_EMPTY_S:
                        old_dev = self.socket_device.get(sk)
                        self.socket_state[sk] = SOCKET_STATE_EMPTY
                        self.socket_device[sk] = None
                        self.socket_device_sig[sk] = None
                        logging.info(
                            f"[ORCH][AUTO EMPTY v90] socket{sk} DEVICE_OFF({old_dev}) "
                            f"{age:.1f}s → EMPTY"
                        )

    # ==================================================================
    # ON mapping
    # ==================================================================
    def _identify_socket_for_device(self, dev: str):
        self._identifying = True
        try:
            candidates = [sk for sk in PHYSICAL_SOCKETS if self.socket_state[sk] == SOCKET_STATE_PENDING]

            if not candidates:
                logging.warning(
                    f"[ORCH][ROLLBACK v90] new device {dev} but no PENDING socket. "
                    f"False ON으로 보고 AI active/signature 정리. state={self._state_summary()}"
                )
                self._rollback_engine_device(dev, reason="no pending socket")
                return

            if len(candidates) == 1:
                sk = candidates[0]
                prev = self.socket_device.get(sk)
                reason = "only-candidate" if prev in (None, dev) else f"only-candidate replace {prev}→{dev}"
                self._assign(sk, dev, reason=reason)
                return

            # v97: LP(charger/tv)도 HP 와 동일하게 relay toggle 신호로 물리 위치를 식별한다.
            # 이전 v90/v91 은 "최근 켠 PENDING 소켓" 순서로 LP 를 배정했는데, 이는 사용자
            # 행동 순서라는 외부 힌트에 의존해 "전류 신호만으로 식별"하는 NILM 취지에 어긋난다
            # (짜고 치기). 제거하고 신호 기반 toggle-id 로 통합. 신호로 구분 안 되면 임의 배정
            # 대신 rollback(정직). LP 가 HP 노이즈에 묻힐 위험은 toggle valid 임계(sig 매칭)로
            # 완화하고, 그래도 모호하면 식별 실패(rollback)로 처리한다.
            chosen = self._toggle_identify(candidates, dev)
            if chosen is None:
                logging.warning(
                    f"[ORCH][ROLLBACK v90] toggle-id failed for {dev}; "
                    f"임의 fallback 배정 금지. candidates={candidates}, state={self._state_summary()}"
                )
                self._rollback_engine_device(dev, reason="toggle identify failed")
                return

            self._assign(chosen, dev, reason="toggle-id")
        finally:
            self._identifying = False

    def _assign(self, sk: int, dev: str, reason: str = "?"):
        # 같은 dev가 다른 socket에 남아 있으면 stale로 보고 정리.
        for other in PHYSICAL_SOCKETS:
            if other == sk:
                continue
            if self.socket_device.get(other) == dev:
                old_state = self.socket_state.get(other)
                self.socket_device[other] = None
                self.socket_device_sig[other] = None
                if old_state != SOCKET_STATE_ASSIGNED:
                    self.socket_state[other] = SOCKET_STATE_EMPTY
                logging.info(
                    f"[ORCH] socket{other} stale {dev} label cleared ({old_state} → {self.socket_state.get(other)})"
                )

        self.socket_state[sk] = SOCKET_STATE_ASSIGNED
        self.socket_device[sk] = dev
        self._socket_pending_time[sk] = 0.0
        self._socket_pending_seq[sk] = 0
        self._socket_pending_source[sk] = ""
        self.last_event = f"assigned {dev} → socket{sk} ({reason})"
        logging.info(f"[ORCH] {self.last_event}")

    def _rollback_engine_device(self, dev: str, reason: str = ""):
        try:
            self.engine.active_devices.pop(dev, None)
            self.engine.device_signatures.pop(dev, None)
            if hasattr(self.engine, "device_on_frames"):
                self.engine.device_on_frames.pop(dev, None)
            if hasattr(self.engine, "device_on_wallclock"):
                self.engine.device_on_wallclock.pop(dev, None)

            # v88: rollback된 dev가 AIEngine 내부 SocketFSM에 DEVICE_ON으로 남으면
            # 다음 low-power 기기, 특히 TV ON 때 내부 슬롯이 꽉 차 [ON FAIL]이 발생한다.
            # 물리 매핑은 orchestrator가 관리하므로, rollback 대상 dev의 내부 슬롯도 같이 비운다.
            cleaned = []
            try:
                for sk_obj in getattr(self.engine, "sockets", []) or []:
                    if getattr(sk_obj, "device", None) == dev:
                        if hasattr(sk_obj, "reset_to_empty"):
                            sk_obj.reset_to_empty()
                        else:
                            sk_obj.state = "EMPTY"
                            sk_obj.device = None
                            sk_obj.power_w = 0.0
                        cleaned.append(getattr(sk_obj, "idx", "?"))
                if cleaned:
                    logging.info(
                        f"[ORCH][ROLLBACK AI-SOCKET CLEAN v88] {dev} stale internal socket(s) {cleaned} → EMPTY"
                    )
            except Exception as exc:  # noqa: BLE001
                logging.warning(f"[ORCH][ROLLBACK AI-SOCKET CLEAN v88] failed: {exc}")

            # v86: AIEngine은 ON 등록 직후 baseline을 새 부하까지 포함한 값으로 sync한다.
            # toggle-id 실패로 rollback만 하고 baseline을 그대로 두면, 실제 기기가 꽂혀 있어도
            # 다음 ON 이벤트가 다시 안 뜨고 PENDING만 유지된다.
            # 따라서 등록 직전 pre-event baseline으로 되돌려 재검출이 가능하게 한다.
            pre_feat = getattr(self.engine, "pre_event_baseline_feat", None)
            if pre_feat:
                try:
                    self.engine.baseline_feat = dict(pre_feat)
                    self.engine.baseline_irms = float(getattr(self.engine, "pre_event_baseline_irms", self.engine.baseline_irms))
                    self.engine.baseline_h1 = float(getattr(self.engine, "pre_event_baseline_h1", self.engine.baseline_h1))
                    logging.info(
                        f"[ORCH][ROLLBACK BASELINE v90] restored pre-event baseline "
                        f"Irms={self.engine.baseline_irms:.1f}, H1={self.engine.baseline_h1:.1f}"
                    )
                except Exception as exc:  # noqa: BLE001
                    logging.warning(f"[ORCH][ROLLBACK BASELINE v90] restore failed: {exc}")
            if hasattr(self.engine, "event_cooldown"):
                self.engine.event_cooldown = max(int(getattr(self.engine, "event_cooldown", 0)), 8)
            logging.info(f"[ORCH][ROLLBACK v90] AI active '{dev}' removed ({reason})")
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[ORCH][ROLLBACK v90] failed for {dev}: {e}")

    def relabel_device(self, old_dev: str, new_dev: str):
        changed = []
        for sk in PHYSICAL_SOCKETS:
            if self.socket_device[sk] == old_dev:
                self.socket_device[sk] = new_dev
                changed.append(sk)
        if old_dev in self._prev_active:
            self._prev_active.discard(old_dev)
            self._prev_active.add(new_dev)
        if changed:
            self.last_event = f"relabel {old_dev} → {new_dev} on socket(s) {changed}"
            logging.info(f"[ORCH] {self.last_event}")

    # ==================================================================
    # Toggle identify for ON
    # ==================================================================
    def _wait_new_frames(self, n_frames: int) -> bool:
        ok = 0
        for _ in range(n_frames):
            try:
                with self.engine_lock:
                    self.engine.process_ai_frame()
                ok += 1
            except Exception as e:  # noqa: BLE001
                logging.warning(f"[ORCH] direct process_ai_frame failed: {e}")
                break
        return ok >= n_frames

    # v97: _choose_low_power_pending_fifo 제거. LP 도 _toggle_identify 신호 기반 식별로 통합.

    def _toggle_average_metrics(self, n_frames: int, exclude_first: int = 0, label: str = "") -> Tuple[float, float, float, bool]:
        # v99: H5_300_mag 평균도 반환 (이전 v98 의 PF 대체). PF 는 intensive(비율)라 LP 하나 꺼도
        # 전체 PF 가 거의 안 변해 토글 diff 로 측정 불가했음. H5 는 extensive(가산)고, HP 의 H5
        # frame 노이즈가 H1 보다 훨씬 작아(SUMMARY: HP H1 std합 15143 vs H5 std합 564) charger
        # H5 신호(597)의 토글 SNR 이 1.06 (H1 의 0.055 대비 19배). LP 위치 식별의 강한 단서.
        i_samples = []
        h_samples = []
        h5_samples = []
        for k in range(n_frames):
            try:
                with self.engine_lock:
                    self.engine.process_ai_frame()
            except Exception as e:  # noqa: BLE001
                logging.warning(f"[ORCH] {label} process_ai_frame failed: {e}")
                continue
            if k < exclude_first:
                continue
            feats = getattr(self.engine, "frame_feats", None)
            if not feats:
                continue
            latest = feats[-1]
            try:
                i_samples.append(float(latest.get("Irms_adc", latest.get("Irms_adc_mean", 0.0))))
                h_samples.append(float(latest.get("H1_60_mag", latest.get("H1_60_mag_mean", 0.0))))
                h5_samples.append(float(latest.get("H5_300_mag", latest.get("H5_300_mag_mean", 0.0))))
            except Exception:  # noqa: BLE001
                pass
        if not i_samples:
            return 0.0, 0.0, 0.0, False
        h5_avg = float(np.mean(h5_samples)) if h5_samples else 0.0
        return float(np.mean(i_samples)), float(np.mean(h_samples)), h5_avg, True

    def _mute_engine(self, frames: int):
        try:
            self.engine.event_cooldown = max(int(getattr(self.engine, "event_cooldown", 0)), int(frames))
        except Exception:  # noqa: BLE001
            pass

    def _toggle_identify(self, candidates: List[int], dev: str) -> Optional[int]:
        original_cooldown = int(getattr(self.engine, "event_cooldown", 0))
        results = {}
        try:
            for sk in candidates:
                self._mute_engine(ENGINE_MUTE_FRAMES)
                i_before, h_before, h5_before, _ = self._toggle_average_metrics(TOGGLE_N_BEFORE, label=f"S{sk}-before")
                self.relay.set(sk, False)
                i_off, h_off, h5_off, got = self._toggle_average_metrics(
                    TOGGLE_N_OFF, exclude_first=TOGGLE_EXCLUDE_FIRST, label=f"S{sk}-off"
                )
                self.relay.set(sk, True)
                self._toggle_average_metrics(TOGGLE_N_RESTORE, label=f"S{sk}-restore")

                diff_i = i_before - i_off
                diff_h = h_before - h_off
                # v99: LP 소켓을 끄면 그 기기 H5 만큼 전체 H5 감소(diff_h5 양수). HP H5 노이즈는
                # 작아(std합 564) charger 의 H5 신호(597)가 H1 보다 19배 강한 SNR 로 비져나온다.
                diff_h5 = h5_before - h5_off
                results[sk] = (diff_i, diff_h, diff_h5, got)
                logging.info(
                    f"[ORCH][TOGGLE-ID v99] dev={dev} socket{sk}: "
                    f"diff_I={diff_i:+.1f}, diff_H1={diff_h:+.1f}, diff_H5={diff_h5:+.1f}, "
                    f"i_b_avg={i_before:.1f}, i_off_avg={i_off:.1f}"
                )

            sig = getattr(self.engine, "device_signatures", {}).get(dev, {}) or {}
            sig_i = abs(float(sig.get("delta_irms", 0.0)))
            sig_h = abs(float(sig.get("delta_h1", 0.0)))
            sig_h5 = abs(float(sig.get("delta_h5", 0.0)))  # v99: H5 sig (ON 시 양수 증가분)

            scored = []
            for sk, (di, dh, dh5, got) in results.items():
                if not got:
                    continue
                if di < -3.0 and dh < TOGGLE_MIN_ABS_H1:
                    continue

                presence_i = di / sig_i if sig_i > 0.5 else 0.0
                presence_h = dh / sig_h if sig_h > 50.0 else 0.0
                # v99: H5 단서. LP 끄면 diff_h5 양수, sig_h5 양수 → presence_h5 양수. HP 의 H5
                # frame 노이즈가 H1 보다 훨씬 작아 charger 검출에 H1 보다 강건(SNR 1.06 vs 0.055).
                presence_h5 = dh5 / sig_h5 if sig_h5 > 30.0 else 0.0

                if dev in LOW_POWER_DEVICES:
                    # 저전력: H1 + H5 동시 단서. H5 는 HP 노이즈에 강건해 charger 위치 검출 강화.
                    score = max(presence_i, 0.0) * 0.30 + max(presence_h, 0.0) * 0.35 + max(presence_h5, 0.0) * 0.35
                    # v97: 빈 소켓 노이즈 배제 위해 sig 매칭 강화 (dh ≥ sig_h*0.25→0.40).
                    # v99: H5 강매치(charger)도 valid 통과 경로 추가 (sig_h5 충분할 때만).
                    valid = (di >= -8.0 and dh >= max(TOGGLE_MIN_ABS_H1, sig_h * 0.40)) \
                        or di >= max(TOGGLE_MIN_ABS_I, sig_i * 0.45) \
                        or (sig_h5 > 30.0 and dh5 >= sig_h5 * 0.40)
                else:
                    score = max(presence_i, 0.0) * 0.65 + max(presence_h, 0.0) * 0.35
                    valid = di >= max(TOGGLE_MIN_ABS_I, sig_i * TOGGLE_MIN_PRESENCE_RATIO)

                if valid:
                    scored.append((sk, score, di, dh))

            if not scored:
                logging.warning(f"[ORCH][TOGGLE-ID v90] no reliable candidate for {dev}; results={results}")
                return None

            scored.sort(key=lambda x: -x[1])
            best = scored[0]
            if len(scored) >= 2 and scored[1][1] >= best[1] * TOGGLE_AMBIG_RATIO:
                logging.warning(
                    f"[ORCH][TOGGLE-ID v90] ambiguous {dev}: "
                    f"best=S{best[0]} score={best[1]:.2f}, second=S{scored[1][0]} score={scored[1][1]:.2f}"
                )

                # v97: 신호로 구분 안 됨(ambiguous) → 외부힌트/임의 배정 대신 rollback(정직).
                return None

            logging.info(
                f"[ORCH][TOGGLE-ID v90] selected socket{best[0]} for {dev} "
                f"score={best[1]:.2f}, diff_I={best[2]:+.1f}, diff_H1={best[3]:+.1f}"
            )
            return best[0]
        finally:
            try:
                self.engine.event_cooldown = max(original_cooldown, int(getattr(self.engine, "event_cooldown", 0)))
            except Exception:  # noqa: BLE001
                pass

    # ==================================================================
    # OFF handling / verification
    # ==================================================================
    def _handle_device_off(self, dev: str):
        for sk, mapped in list(self.socket_device.items()):
            if mapped == dev and self.socket_state.get(sk) == SOCKET_STATE_ASSIGNED:
                self._snapshot_socket_signature_unlocked(sk, dev)
                try:
                    self.relay.set(sk, False)
                except Exception as e:  # noqa: BLE001
                    logging.warning(f"[ORCH] relay.set({sk},False) failed: {e}")
                self.socket_state[sk] = SOCKET_STATE_DEVICE_OFF
                self._socket_off_time[sk] = time.perf_counter()
                self.last_event = f"{dev} OFF → socket{sk} relay OFF (standby cut)"
                logging.info(f"[ORCH] {self.last_event}")
                return
        logging.warning(f"[ORCH] {dev} OFF detected but no ASSIGNED physical socket mapping")

    def _off_verify_callback(self, dev, drop, win_feat):
        if dev is None:
            return "cancel"

        now_t = time.perf_counter()
        if now_t - self._off_verify_last_callback_t > 1.0:
            self._off_verify_reject_ratios.clear()
        self._off_verify_last_callback_t = now_t

        # lock-free snapshot. callback은 AIEngine frame 처리 중 호출될 수 있으므로 deadlock 방지.
        socket_device_snap = dict(self.socket_device)
        socket_state_snap = dict(self.socket_state)
        sk = None
        for s, mapped in socket_device_snap.items():
            if mapped == dev and socket_state_snap.get(s) == SOCKET_STATE_ASSIGNED:
                sk = s
                break

        if sk is None:
            logging.warning(f"[ORCH][OFF-VERIFY v89] {dev} assigned socket 없음 → cancel")
            self._remove_engine_active_unlocked(dev, reason="off verify no mapping")
            return "cancel"

        self._mute_engine(ENGINE_MUTE_FRAMES)

        try:
            i_before, h_before = self._baseline_verify_metrics(win_feat)
            if i_before is None:
                logging.warning(f"[ORCH][OFF-VERIFY v89] {dev} before 측정 실패 → cancel")
                return "cancel"

            self.relay.set(sk, False)
            time.sleep(OFF_VERIFY_SETTLE_S)

            samples_i = []
            samples_h = []
            deadline = time.perf_counter() + OFF_VERIFY_RELAY_GAP_S
            while time.perf_counter() < deadline:
                m = self._measure_raw_metrics()
                if m is not None:
                    samples_i.append(m[0])
                    samples_h.append(m[1])
                time.sleep(0.02)

            if not samples_i:
                logging.warning(f"[ORCH][OFF-VERIFY v89] {dev} off 측정 실패 → cancel")
                return "cancel"

            i_off = float(np.mean(samples_i))
            h_off = float(np.mean(samples_h)) if samples_h else 0.0
            i_std = float(np.std(samples_i)) if len(samples_i) >= 2 else 0.0
            h_std = float(np.std(samples_h)) if len(samples_h) >= 2 else 0.0

            diff_i = i_before - i_off
            diff_h = (h_before or 0.0) - h_off

            sig = getattr(self.engine, "device_signatures", {}).get(dev, {}) or {}
            sig_i = abs(float(sig.get("delta_irms", 0.0)))
            sig_h = abs(float(sig.get("delta_h1", 0.0)))
            ratio_i = diff_i / sig_i if sig_i > 0.5 else 0.0
            ratio_h = diff_h / sig_h if sig_h > 50.0 else 0.0

            logging.info(
                f"[ORCH][OFF-VERIFY v89] {dev} socket{sk}: "
                f"I_before={i_before:.1f}, I_off={i_off:.1f}, ΔI={diff_i:+.1f}, "
                f"H1_before={(h_before or 0.0):.1f}, H1_off={h_off:.1f}, ΔH1={diff_h:+.1f}, "
                f"sig_I={sig_i:.1f}, sig_H1={sig_h:.1f}, "
                f"ratio_I={ratio_i:.2f}, ratio_H1={ratio_h:.2f}, "
                f"std_I={i_std:.1f}, std_H1={h_std:.1f}, samples={len(samples_i)}"
            )

            # v87: 측정 std가 크다는 이유만으로 confirm하지 않는다.
            # v85/v86에서는 noisy sample을 confirm fallback으로 처리해서,
            # 실제로 살아있는 LP 기기를 OFF로 확정할 위험이 있었다.
            # 이제는 std가 커도 아래 ratio 기반 판단을 그대로 수행한다.
            if len(samples_i) >= OFF_VERIFY_MIN_SAMPLES and i_std >= OFF_VERIFY_NOISE_STD_LIMIT:
                logging.info(
                    f"[ORCH][OFF-VERIFY v89] noisy samples std_I={i_std:.1f} ≥ "
                    f"{OFF_VERIFY_NOISE_STD_LIMIT:.1f} → ratio/H1 판단 계속"
                )

            # v92: LP(charger/tv) + HP active 전용 분기. HP 대전류 노이즈가 작은 LP sig 를
            # 가려 일반 ratio 판정이 불가능하다. 살아있는 LP 만 그 소켓 토글 시 sig 만큼 빠져
            # ratio≈1.0 (residual band) 를 만든다. 뽑힌 LP 는 ΔI/ΔH1 이 HP 노이즈만이라
            # ratio 가 band 밖 (REJECT 미만 또는 OVERSHOOT 초과). 실측 (2026-05-31 01:37:25):
            # charger 뽑음 ratio_I=2.22/ratio_H1=3.74 (OVERSHOOT 초과) 를 v89 가 still present
            # 로 오판 → reject → 영구 미인식. tv 뽑음 ratio 0.5~0.6 (REJECT 미만) 도 ambiguous
            # LP 로 reject. band 밖이면 absent → confirm. HARD 초과만 reject 유지.
            active_now = dict(getattr(self.engine, "active_devices", {}) or {})
            hp_active = any(d in HIGH_POWER_DEVICES for d in active_now)
            if dev in LOW_POWER_DEVICES and hp_active:
                hard_i = sig_i > 0.5 and ratio_i > OFF_VERIFY_RESIDUAL_RATIO_HARD
                hard_h = sig_h > 50.0 and ratio_h > OFF_VERIFY_RESIDUAL_RATIO_HARD
                if hard_i or hard_h:
                    self._off_verify_reject_ratios[dev] = max(ratio_i, ratio_h)
                    logging.info(
                        f"[ORCH][OFF-VERIFY FALSE v92] {dev} HP-amid large residual "
                        f"ratio_I={ratio_i:.2f} ratio_H1={ratio_h:.2f} → reject"
                    )
                    return "reject"
                band_i = (sig_i > 0.5
                          and OFF_VERIFY_RESIDUAL_RATIO_REJECT <= ratio_i <= OFF_VERIFY_RESIDUAL_RATIO_OVERSHOOT)
                band_h = (sig_h > 50.0
                          and OFF_VERIFY_RESIDUAL_RATIO_REJECT <= ratio_h <= OFF_VERIFY_RESIDUAL_RATIO_OVERSHOOT)
                if band_i or band_h:
                    self._off_verify_reject_ratios[dev] = max(ratio_i, ratio_h)
                    logging.info(
                        f"[ORCH][OFF-VERIFY FALSE v92] {dev} HP-amid residual band "
                        f"ratio_I={ratio_i:.2f} ratio_H1={ratio_h:.2f} → still present, reject"
                    )
                    return "reject"
                logging.info(
                    f"[ORCH][OFF-VERIFY v92] {dev} HP-amid off-band "
                    f"ratio_I={ratio_i:.2f} ratio_H1={ratio_h:.2f} → absent, confirm"
                )
                return "confirm"

            # still present 판단: relay를 껐을 때 해당 기기 signature에 준하는 변화가 나오면
            # 그 기기는 아직 연결/동작 중인 것.
            still_by_i = False
            still_by_h = False
            if sig_i > 0.5:
                still_by_i = ratio_i >= OFF_VERIFY_RESIDUAL_RATIO_REJECT
            else:
                still_by_i = diff_i >= OFF_VERIFY_MIN_DELTA_I

            if sig_h > 50.0:
                still_by_h = ratio_h >= OFF_VERIFY_RESIDUAL_RATIO_REJECT
            else:
                still_by_h = diff_h >= OFF_VERIFY_MIN_DELTA_H1

            # 저전력은 I가 작으므로 H1 또는 I 중 하나만 강해도 reject.
            # 고전력은 I/H1 둘 중 하나가 signature에 충분히 맞으면 reject.
            if still_by_i or (dev in LOW_POWER_DEVICES and still_by_h):
                self._off_verify_reject_ratios[dev] = max(ratio_i, ratio_h)
                logging.info(f"[ORCH][OFF-VERIFY FALSE v89] {dev} still present → reject")
                return "reject"

            # absent 판단: I/H1 모두 낮으면 진짜 빠진 것.
            confirm_by_ratio = True
            if sig_i > 0.5 and ratio_i >= OFF_VERIFY_RESIDUAL_RATIO_CONFIRM:
                confirm_by_ratio = False
            if dev in LOW_POWER_DEVICES and sig_h > 50.0 and ratio_h >= OFF_VERIFY_RESIDUAL_RATIO_CONFIRM:
                confirm_by_ratio = False

            if confirm_by_ratio:
                return "confirm"

            # v87: LP(charger/tv)는 애매하면 끄지 않는다.
            # LP는 전류가 작아서 HP 노이즈와 섞이면 ratio가 중간값이 되기 쉽다.
            # 강한 잔존 증거는 reject, 명확한 부재는 confirm, 중간값은 reject해서 cascade를 막는다.
            if dev in LOW_POWER_DEVICES:
                self._off_verify_reject_ratios[dev] = max(ratio_i, ratio_h)
                logging.info(f"[ORCH][OFF-VERIFY v89] ambiguous LP {dev} → reject")
                return "reject"

            # 고출력은 애매해도 기존 정책대로 confirm.
            logging.info(f"[ORCH][OFF-VERIFY v89] ambiguous HP {dev} but no strong residual → confirm")
            return "confirm"
        finally:
            try:
                self.relay.set(sk, True)
            except Exception:  # noqa: BLE001
                pass

    def _off_verify_exhaust_fallback(self, drop, win_feat, excluded):
        """모든 후보가 reject된 경우 전체 ASSIGNED 소켓을 토글해 실제 absent 후보 탐색."""
        targets = [
            (sk, self.socket_device.get(sk))
            for sk in PHYSICAL_SOCKETS
            if self.socket_state.get(sk) == SOCKET_STATE_ASSIGNED and self.socket_device.get(sk)
        ]
        if not targets:
            return None

        logging.info(f"[ORCH][OFF-VERIFY-EXHAUST v89] start targets={targets}, excluded={sorted(excluded)}")
        absent = []
        for sk, dev in targets:
            sig = getattr(self.engine, "device_signatures", {}).get(dev, {}) or {}
            sig_i = abs(float(sig.get("delta_irms", 0.0)))
            sig_h = abs(float(sig.get("delta_h1", 0.0)))

            i_before, h_before = self._baseline_verify_metrics(win_feat)
            if i_before is None:
                continue

            try:
                self.relay.set(sk, False)
                time.sleep(OFF_VERIFY_SETTLE_S)
                samples_i = []
                samples_h = []
                deadline = time.perf_counter() + OFF_VERIFY_RELAY_GAP_S
                while time.perf_counter() < deadline:
                    m = self._measure_raw_metrics()
                    if m is not None:
                        samples_i.append(m[0])
                        samples_h.append(m[1])
                    time.sleep(0.02)
            finally:
                try:
                    self.relay.set(sk, True)
                except Exception:  # noqa: BLE001
                    pass

            if not samples_i:
                continue
            i_off = float(np.mean(samples_i))
            h_off = float(np.mean(samples_h)) if samples_h else 0.0
            diff_i = i_before - i_off
            diff_h = (h_before or 0.0) - h_off
            i_std = float(np.std(samples_i)) if len(samples_i) >= 2 else 0.0
            ratio_i = diff_i / sig_i if sig_i > 0.5 else 0.0
            ratio_h = diff_h / sig_h if sig_h > 50.0 else 0.0
            ratio = max(ratio_i, ratio_h if dev in LOW_POWER_DEVICES else 0.0)

            logging.info(
                f"[ORCH][OFF-VERIFY-EXHAUST v89] {dev}@S{sk}: "
                f"ΔI={diff_i:+.1f}, ΔH1={diff_h:+.1f}, "
                f"ratio_I={ratio_i:.2f}, ratio_H1={ratio_h:.2f}, std_I={i_std:.1f}"
            )

            if ratio < OFF_VERIFY_FALLBACK_RATIO_ABSENT and i_std < OFF_VERIFY_NOISE_STD_LIMIT:
                # 직전에 reject된 기기가 relay cycle 후 standby로 보이는 경우는 제외.
                prior_reject = self._off_verify_reject_ratios.get(dev, 0.0)
                if dev in excluded and prior_reject >= 1.0:
                    logging.info(
                        f"[ORCH][OFF-VERIFY-EXHAUST v89] skip {dev}@S{sk}: "
                        f"prior reject ratio={prior_reject:.2f} suggests standby corruption"
                    )
                    continue
                absent.append((dev, sk, ratio))

        if not absent:
            return None

        # drop signature와 가장 가까운 absent 후보 선택.
        def match_score(entry):
            dev, _, _ = entry
            sig = getattr(self.engine, "device_signatures", {}).get(dev, {}) or {}
            s_i = abs(float(sig.get("delta_irms", 0.0)))
            s_h = abs(float(sig.get("delta_h1", 0.0)))
            d_i = abs(float(drop.get("delta_irms", 0.0)))
            d_h = abs(float(drop.get("delta_h1", 0.0)))
            score = 0.0
            if s_i > 0.5:
                score += abs(d_i / s_i - 1.0)
            if s_h > 50.0:
                score += abs(d_h / s_h - 1.0)
            return score

        absent.sort(key=match_score)
        dev, sk, ratio = absent[0]
        logging.info(f"[ORCH][OFF-VERIFY-EXHAUST v89] selected absent {dev}@S{sk}, ratio={ratio:.2f}")
        return dev

    def _baseline_verify_metrics(self, win_feat) -> Tuple[Optional[float], Optional[float]]:
        i_before = None
        h_before = None
        try:
            if win_feat is not None:
                i_before = float(win_feat.get("Irms_adc_mean", win_feat.get("Irms_adc", 0.0)))
                h_before = float(win_feat.get("H1_60_mag_mean", win_feat.get("H1_60_mag", 0.0)))
        except Exception:  # noqa: BLE001
            i_before = None
            h_before = None
        if i_before is None or i_before <= 0:
            m = self._measure_raw_metrics()
            if m is None:
                return None, None
            return m
        return i_before, h_before

    def _measure_raw_metrics(self) -> Optional[Tuple[float, float]]:
        """raw ch1에서 Irms와 60Hz H1 magnitude를 계산."""
        try:
            with self.engine_lock:
                ch0, ch1, ts, fs = self.engine.process_raw_mode()
            x = np.asarray(ch1, dtype=np.float64)
            if x.size == 0:
                return None
            x = x - float(np.mean(x))
            irms = float(np.sqrt(np.mean(x ** 2)))

            fs = float(fs) if fs else 0.0
            if fs <= 0 or x.size < 8:
                return irms, 0.0
            win = np.hanning(x.size)
            spec = np.fft.rfft(x * win)
            freqs = np.fft.rfftfreq(x.size, d=1.0 / fs)
            idx = int(np.argmin(np.abs(freqs - 60.0)))
            h1 = float(np.abs(spec[idx]))
            return irms, h1
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[ORCH][RAW-METRIC v85] measure failed: {e}")
            return None

    # ==================================================================
    # Helpers
    # ==================================================================
    def _assigned_sockets_unlocked(self) -> List[int]:
        return [sk for sk in PHYSICAL_SOCKETS if self.socket_state.get(sk) == SOCKET_STATE_ASSIGNED]

    def _snapshot_socket_signature_unlocked(self, sk: int, dev: Optional[str]):
        if not dev:
            return
        try:
            sig = getattr(self.engine, "device_signatures", {}).get(dev, {}) or {}
            if sig:
                self.socket_device_sig[sk] = {
                    "delta_irms": float(sig.get("delta_irms", 0.0)),
                    "delta_h1": float(sig.get("delta_h1", 0.0)),
                    "delta_pabs": float(sig.get("delta_pabs", 0.0)),
                }
        except Exception:  # noqa: BLE001
            pass

    def _remove_engine_active_unlocked(self, dev: Optional[str], reason: str = ""):
        if not dev:
            return
        try:
            self.engine.active_devices.pop(dev, None)
            if hasattr(self.engine, "event_cooldown"):
                self.engine.event_cooldown = max(int(getattr(self.engine, "event_cooldown", 0)), 10)
            logging.info(f"[ORCH] AI active '{dev}' removed ({reason})")
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[ORCH] AI active remove failed for {dev}: {e}")

    def get_socket_status(self):
        with self.lock:
            return {
                sk: {
                    "state": self.socket_state[sk],
                    "device": self.socket_device[sk],
                }
                for sk in PHYSICAL_SOCKETS
            }

    def _state_summary(self) -> str:
        return ", ".join(
            f"S{sk}:{self.socket_state[sk]}" + (f"({self.socket_device[sk]})" if self.socket_device[sk] else "")
            for sk in PHYSICAL_SOCKETS
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print("This module is intended to be used from main.py")
