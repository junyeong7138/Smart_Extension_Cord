#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
socket_orchestrator.py
======================
물리 4 소켓의 *실제* 매핑을 관리한다.

흐름
----
1. 시작 시 모든 릴레이 OFF (모든 소켓 EMPTY).
2. 사용자가 터치센서 누름 → empty(또는 device_off) 소켓 중 하나의 릴레이 ON
   → 해당 소켓 PENDING (사용자가 기기 꽂을 대기).
3. 사용자 기기 꽂음 → AIEngine 이 ON event 감지 → 기기 분류.
4. Orchestrator 가 polling 으로 새 device 감지.
5. PENDING 소켓들 중 어느 것이 그 기기인지 식별:
   - PENDING 후보가 1개 → 그 소켓에 매핑 (ASSIGNED).
   - PENDING 후보가 2+ → 후보 하나씩 릴레이 짧게 OFF → win_feat 의 Irms 변화 측정 →
     변화 가장 큰 소켓에 매핑.
6. AIEngine 이 device OFF 감지 → 매핑된 물리 소켓 릴레이 OFF (대기전력 차단).
   소켓 state = DEVICE_OFF.
7. 다시 1번부터 (DEVICE_OFF 소켓도 EMPTY 와 동등하게 터치센서로 재활성화 가능).

설계 원칙
---------
- ai_extension_v3.py 는 수정하지 않는다 (분류 로직 보존).
- AIEngine 의 active_devices 와 baseline_irms 를 polling 으로 관찰.
- 토글 식별 동안 AIEngine 의 event_cooldown 을 임시로 올려서 (외부 변수 set)
  AIEngine 이 토글로 인한 OFF event 를 발생시키지 않게 한다.
"""

import logging
import threading
import time

import numpy as np


# =====================================================================
# 설정
# =====================================================================
PHYSICAL_SOCKETS = [1, 2, 3, 4]

# 소켓 state
SOCKET_STATE_EMPTY = "EMPTY"             # 릴레이 OFF, 기기 없음
SOCKET_STATE_PENDING = "PENDING"         # 릴레이 ON, 기기 꽂힐 대기 또는 식별 대기
SOCKET_STATE_ASSIGNED = "ASSIGNED"       # 식별 완료, 기기 매핑 됨
SOCKET_STATE_DEVICE_OFF = "DEVICE_OFF"   # 매핑된 기기가 꺼짐, 릴레이 이미 OFF

# 식별 토글 파라미터
IDENTIFY_TOGGLE_GAP_S = 0.30    # 릴레이 OFF 후 기본 대기 (frame 단위 갱신 기대)
IDENTIFY_NEW_FRAMES_REQUIRED = 3   # 토글 후 최소 N개 새 frame 도착 후 측정 (이전 frame 캐시 회피)
IDENTIFY_MAX_WAIT_S = 1.50      # 새 frame 대기 최대 시간 (SPI 지연 안전 마진)
IDENTIFY_MIN_DIFF_IRMS = 5.0    # 신뢰 가능한 식별을 위한 최소 ΔIrms

# AIEngine 의 event_cooldown 을 토글 동안 강제로 올림 (OFF event 발생 방지)
ENGINE_MUTE_FRAMES = 30

# v2: OFF 전수 스캔 파라미터.
# off_suspect 가 뜨면 ASSIGNED 소켓을 하나씩 relay OFF → ΔH1 측정 → 부재/잔존 판정.
# 릴레이 토글이 물리적 진실이라 signature 추측이 필요 없다.
OFF_VERIFY_SETTLE_S = 0.05        # relay 동작 후 측정 전 안정화 대기 (_toggle_average_metrics 도 사용)
SCAN_N_BEFORE = 4                 # 토글 직전 baseline 측정 frame 수
SCAN_N_OFF = 6                    # 토글 OFF 상태 측정 frame 수 (duty 1~2 cycle 커버)
SCAN_EXCLUDE_FIRST = 1            # relay 전이 직후 1 frame 은 settle 중 → 평균 제외
SCAN_N_RESTORE = 2                # 복원 후 안정화 frame 수
# ΔH1 ratio = (h1_before - h1_off) / sig_dh1.
# 부재(이미 빠짐): relay OFF 해도 H1 거의 안 빠짐 → ratio≈0.  잔존(살아있음): ratio≈1.
# 실측(v80): 살아있는 기기 0.95~1.23, 부재 0.01~0.07 → 0.30 경계 안전. H1 SNR 압도적(128:1).
OFF_CONFIRM_RATIO = 0.30          # |ratio_h1| < 0.30 → 부재 = OFF 확정
MIN_SIG_H1 = 50.0                 # sig_dh1 신뢰 하한 (이하면 Irms fallback)
OFF_VERIFY_MIN_DELTA_I = 5.0      # Irms 판정 절대 임계
OFF_SCAN_REMAIN_STOP = 300.0      # shortfall 잔량이 이 이하로 떨어지면 스캔 조기 종료
# v2.1: H1 측정 교란(거대 음수 ratio) 시 ΔI 보조 판정 임계 (sig_di 대비 비율).
# 작은 LP 소켓 토글이 같은 계통 큰 HP 의 H1 을 출렁이게 하는 교란 대응.
OFF_SCAN_IRMS_PRESENT_RATIO = 0.50  # ΔI ≥ 0.5·sig_di → 잔존
OFF_SCAN_IRMS_ABSENT_RATIO = 0.25   # ΔI < 0.25·sig_di → 부재

# Polling 간격
MONITOR_INTERVAL_S = 0.2

# LP RAMP CONTINUATION swap 감지 (AIEngine 측 v52d 와 짝)
# 한 tick 안에 LP 한 개가 사라지고 다른 LP 한 개가 등장하면 1:1 swap 패턴으로 인식해
# socket_device 라벨만 교체, relay/state 는 그대로 유지 (DEVICE OFF 와 new identify 둘 다 skip).
LOW_POWER_DEVICES = frozenset({"charger", "tv"})
# v70: HP OFF 직후 baseline drift 가 cond2 ON 으로 잘못 트리거되어 chosen=LP 로 가짜
# 등록되는 사례 (실측 2026-05-29 18:44:40 microwave OFF 후 10초 → 가짜 tv 등록). 이
# cooldown 안에 새 LP dev 가 active 에 추가되면 false positive 로 보고 거부.
HIGH_POWER_DEVICES = frozenset({"dryer", "microwave", "cleaner"})
LP_AFTER_HP_OFF_COOLDOWN_S = 15.0


class SocketOrchestrator:
    """터치센서 + AIEngine + RelayController 사이의 orchestration.

    AIDashboardUI / mobile_ui 에서 get_socket_status() 로 표시.
    """

    def __init__(self, relay_controller, ai_engine, lock=None):
        self.relay = relay_controller
        self.engine = ai_engine
        self.lock = lock or threading.RLock()
        # v37: SPI 자원 동시 접근 방지용 lock. socket_dashboard 와 공유해서
        # main thread (matplotlib animation) 와 orchestrator thread 가 동시에
        # process_ai_frame() 을 호출하지 않도록 보호.
        self.engine_lock = threading.RLock()

        # 물리 소켓 상태 / 매핑
        self.socket_state = {i: SOCKET_STATE_EMPTY for i in PHYSICAL_SOCKETS}
        self.socket_device = {i: None for i in PHYSICAL_SOCKETS}
        # v63: DEVICE_OFF 직전의 device signature snapshot. 자동 복원 시 현재 sig 와의
        # 동조율 비교용. {sk: {"delta_irms": .., "delta_h1": .., "delta_pabs": ..}}
        self.socket_device_sig = {i: None for i in PHYSICAL_SOCKETS}

        # v70: 직전 HP device OFF 시각. LP dev 가짜 등록 cooldown 용.
        self._last_hp_off_t = 0.0

        # AIEngine 의 active_devices snapshot (이전 monitor tick 시점)
        self._prev_active = set()

        # 동기화: 식별 진행 중에는 monitor 가 새 변화 받지 않음
        self._identifying = False

        # 통계
        self.last_event = None

        self._stop = threading.Event()
        self._thread = None

        # 시작 시 모든 릴레이 OFF (안전)
        try:
            self.relay.all_off()
            logging.info("[ORCH] init: all relays OFF (safe state)")
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[ORCH] init all_off failed: {e}")

        # AIEngine 의 process_ai_frame 을 wrap 해서 매 frame win_feat 을 저장.
        # ai_engine_v2.py 는 수정하지 않고 외부에서 monkey-patch.
        # 이게 없으면 토글 식별 시 baseline_irms(EMA) 만 보여서 변화 detect 불가능.
        self._patch_engine_for_win_feat_capture()

        # v2: OFF 콜백 주입 제거. AIEngine 은 off_suspect flag 만 세우고, OFF 결정은
        # monitor loop 의 _check_off_suspect → _full_scan_off (전수 릴레이 토글) 가 한다.

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

    # =====================================================================
    # 외부 API: touch press
    # =====================================================================
    def on_touch(self):
        """터치센서 콜백.

        한 번의 터치로 EMPTY/DEVICE_OFF 상태인 *모든* 소켓의 릴레이를 동시에 ON → PENDING.
        ASSIGNED/PENDING 소켓은 그대로 둔다.
        반환: 새로 활성화된 소켓 인덱스 리스트 (없으면 빈 리스트).
        """
        with self.lock:
            activated = []
            for sk in PHYSICAL_SOCKETS:
                state = self.socket_state[sk]
                if state in (SOCKET_STATE_EMPTY, SOCKET_STATE_DEVICE_OFF):
                    self.relay.set(sk, True)
                    self.socket_state[sk] = SOCKET_STATE_PENDING
                    # v62: DEVICE_OFF 의 이전 device 라벨은 보존 (자동 복원 비교용).
                    # EMPTY 는 한 번도 매핑된 적 없으니 None.
                    if state == SOCKET_STATE_EMPTY:
                        self.socket_device[sk] = None
                    # DEVICE_OFF 케이스: socket_device[sk] 그대로 유지 → _identify_socket_for_device
                    # 에서 새 device label 이 보존된 라벨과 같으면 자동 복원, 다르면 새로 갱신.
                    activated.append(sk)

            if activated:
                self.last_event = f"touch → sockets {activated} relay ON (PENDING, 일괄 활성화)"
                logging.info(f"[ORCH] {self.last_event}")
            else:
                self.last_event = "touch ignored - no EMPTY/DEVICE_OFF socket"
                logging.info(f"[ORCH] {self.last_event} ({self._state_summary()})")
            return activated

    # =====================================================================
    # 외부 API: mobile UI 등 외부 relay 변경 동기화 (v65)
    # =====================================================================
    def on_external_relay_change(self, sk):
        """mobile UI 같은 외부 컴포넌트가 relay 를 직접 켜고/끈 후 호출.

        relay 의 실제 상태를 읽어서 socket_state 를 동기화. on_touch 와 달리 단일 socket
        대상이고 토글 양방향 모두 지원. v64 의 라벨 매칭/위치 검증 분기가 정상 작동하려면
        DEVICE_OFF 가 PENDING 으로 올바르게 전환돼야 한다는 사실에 기반.

        state 전이 규칙:
          relay ON  + EMPTY/DEVICE_OFF → PENDING (라벨/sig 보존, on_touch 동작과 동일)
          relay ON  + 그 외             → 변화 없음
          relay OFF + ASSIGNED          → DEVICE_OFF (라벨 보존, OFF 직전 sig snapshot 저장)
          relay OFF + PENDING           → 라벨 있으면 DEVICE_OFF, 없으면 EMPTY
          relay OFF + 그 외             → 변화 없음
        """
        if sk not in PHYSICAL_SOCKETS:
            return
        with self.lock:
            try:
                actual_on = bool(self.relay.get_state().get(sk, False))
            except Exception as e:  # noqa: BLE001
                logging.warning(f"[ORCH] external relay sync: relay state 읽기 실패: {e}")
                return

            cur = self.socket_state.get(sk)

            if actual_on:
                if cur in (SOCKET_STATE_EMPTY, SOCKET_STATE_DEVICE_OFF):
                    self.socket_state[sk] = SOCKET_STATE_PENDING
                    # 라벨/sig 그대로 유지 (DEVICE_OFF 였으면 보존된 라벨 → v64 분기 진입)
                    logging.info(
                        f"[ORCH] external relay ON socket{sk}: {cur} → PENDING "
                        f"(preserved label={self.socket_device.get(sk)})"
                    )
                # ASSIGNED/PENDING 이면 변화 없음 (이미 ON 상태)
            else:
                if cur == SOCKET_STATE_ASSIGNED:
                    dev = self.socket_device.get(sk)
                    # OFF 직전 sig snapshot (자동 복원 비교용, _handle_device_off 와 동일)
                    try:
                        if dev:
                            sig = self.engine.device_signatures.get(dev, {})
                            if sig:
                                self.socket_device_sig[sk] = {
                                    "delta_irms": float(sig.get("delta_irms", 0.0)),
                                    "delta_h1":   float(sig.get("delta_h1", 0.0)),
                                    "delta_pabs": float(sig.get("delta_pabs", 0.0)),
                                }
                    except Exception:  # noqa: BLE001
                        pass

                    # v66: AI engine 의 active state 강제 정리. v65 의 socket_state 갱신만
                    # 으로는 AI 가 dev 를 active 로 그대로 보고 → 다음 동일 dev ON 시
                    # already-active 로 무시 + PRE-BASELINE FIX 가 잘못된 expected baseline
                    # 으로 정상 ON 신호를 transient OFF 로 reroute 시킴 (실측 16:02:29~44
                    # microwave 재인식 실패 케이스).
                    try:
                        if dev:
                            self.engine.active_devices.pop(dev, None)
                            # baseline 도 현재 측정값으로 sync (PRE-BASELINE FIX 의 잘못된
                            # active sigs 합 계산 회피).
                            wf = getattr(self.engine, "_latest_win_feat", None)
                            if wf:
                                try:
                                    self.engine.baseline_irms = float(
                                        wf.get("Irms_adc_mean", self.engine.baseline_irms)
                                    )
                                    self.engine.baseline_h1 = float(
                                        wf.get("H1_60_mag_mean", self.engine.baseline_h1)
                                    )
                                except Exception:  # noqa: BLE001
                                    pass
                            logging.info(
                                f"[ORCH] external OFF: AI engine.active_devices['{dev}'] "
                                f"강제 제거 + baseline sync (Irms={self.engine.baseline_irms:.1f}, "
                                f"H1={self.engine.baseline_h1:.1f})"
                            )
                    except Exception as e:  # noqa: BLE001
                        logging.warning(f"[ORCH] AI engine sync 실패: {e}")

                    self.socket_state[sk] = SOCKET_STATE_DEVICE_OFF
                    logging.info(
                        f"[ORCH] external relay OFF socket{sk}: ASSIGNED({dev}) → DEVICE_OFF"
                    )
                elif cur == SOCKET_STATE_PENDING:
                    if self.socket_device.get(sk) is not None:
                        self.socket_state[sk] = SOCKET_STATE_DEVICE_OFF
                        logging.info(
                            f"[ORCH] external relay OFF socket{sk}: PENDING → DEVICE_OFF "
                            f"(label={self.socket_device.get(sk)} 보존)"
                        )
                    else:
                        self.socket_state[sk] = SOCKET_STATE_EMPTY
                        logging.info(
                            f"[ORCH] external relay OFF socket{sk}: PENDING → EMPTY"
                        )
                # EMPTY/DEVICE_OFF 이면 변화 없음 (이미 OFF 상태)

    # =====================================================================
    # Monitoring loop (background thread)
    # =====================================================================
    def start(self):
        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="socket_orch"
        )
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
                    self._check_engine_changes()      # ON 신규 매핑
                    self._check_off_suspect()          # v2: OFF 전수 스캔
            except Exception as e:  # noqa: BLE001
                logging.error(f"[ORCH] monitor error: {e}")
            time.sleep(MONITOR_INTERVAL_S)

    def _check_engine_changes(self):
        """AIEngine.active_devices 변화 감지."""
        with self.lock:
            current_active = set(self.engine.active_devices.keys())
            new_devices = current_active - self._prev_active
            removed_devices = self._prev_active - current_active

            # v52d: LP RAMP CONTINUATION swap 패턴 감지.
            # AIEngine 이 두 LP event 를 같은 가전의 ramp 분할로 판단해 라벨 swap 했을 때
            # active_devices diff 는 (removed={old_lp}, added={new_lp}) 로 보인다.
            # 1:1 LP 교체이고 old_lp 가 이미 매핑돼 있으면 실제 plug 변화가 아니라 라벨 변경.
            # relay OFF / 새 socket 식별 둘 다 skip 하고 socket_device 라벨만 교체.
            # 실측 (2026-05-27 15:01:39 → 15:01:48): charger → tv swap.
            if (len(new_devices) == 1 and len(removed_devices) == 1):
                old_lp = next(iter(removed_devices))
                new_lp = next(iter(new_devices))
                if (old_lp in LOW_POWER_DEVICES and new_lp in LOW_POWER_DEVICES):
                    swapped_sk = None
                    for sk, mapped in self.socket_device.items():
                        if mapped == old_lp:
                            swapped_sk = sk
                            break
                    if swapped_sk is not None:
                        self.socket_device[swapped_sk] = new_lp
                        self.last_event = (
                            f"LP RAMP swap: socket{swapped_sk} {old_lp} → {new_lp} "
                            f"(라벨만 교체, relay 유지)"
                        )
                        logging.info(f"[ORCH] {self.last_event}")
                        new_devices = set()
                        removed_devices = set()

            # v2: removed_devices 의 OFF 처리는 하지 않는다. AIEngine 은 스스로
            # active 에서 기기를 빼지 않으며, OFF 는 _check_off_suspect 의 전수 스캔이
            # confirm_device_off 로 결정한다. (LP swap 패턴은 위에서 라벨 교체로 흡수됨.)

            # 2) 새 device → 물리 소켓 식별
            for dev in new_devices:
                # v76: "이미 매핑" 체크를 ASSIGNED state 만으로 한정.
                # 기존 (`dev in self.socket_device.values()`) 은 DEVICE_OFF 의 보존 라벨도
                # "매핑됨" 으로 간주해서 새 매핑 시도 자체를 막음.
                # 실측 (2026-05-29 23:38:11): 사용자 S2 PENDING + dryer 꽂음 → AI 가 dryer
                # 등록했는데 S4=DEVICE_OFF(dryer 보존 라벨) 때문에 monitor 가 매핑 skip →
                # 사용자 의도 S2 에 dryer 매핑 안 됨 → callback cancel 사이클 반복.
                # ASSIGNED 일 때만 진짜 "이미 매핑". DEVICE_OFF 는 새 매핑/자동 복원 시도해야.
                # (v77 의 _assign 시점 stale 라벨 정리와 결합되어 사용자 의도 "S2 dryer 매핑
                #  + S4 EMPTY" 완전 실현.)
                already_assigned = any(
                    self.socket_device.get(sk) == dev
                    and self.socket_state.get(sk) == SOCKET_STATE_ASSIGNED
                    for sk in PHYSICAL_SOCKETS
                )
                if already_assigned:
                    # 이미 ASSIGNED 매핑된 device 가 active 에 다시 나타남 (RECYCLE 등). 무시.
                    continue
                # v70: HP OFF 직후 LP dev 가짜 등록 보호. HP OFF 후 cooldown 안에 새 LP
                # dev 가 등록 시도되면 baseline drift 의 false positive 로 보고 거부 +
                # AI engine.active_devices 에서도 제거.
                if dev in LOW_POWER_DEVICES:
                    now_t = time.perf_counter()
                    elapsed = now_t - self._last_hp_off_t
                    if elapsed < LP_AFTER_HP_OFF_COOLDOWN_S:
                        logging.warning(
                            f"[ORCH] LP dev '{dev}' detected 직후 HP OFF cooldown 안 "
                            f"(elapsed={elapsed:.1f}s < {LP_AFTER_HP_OFF_COOLDOWN_S}s) → "
                            f"baseline drift false positive 추정, 등록 거부 (active_devices 에서 제거)"
                        )
                        try:
                            self.engine.active_devices.pop(dev, None)
                        except Exception:  # noqa: BLE001
                            pass
                        continue
                self._identify_socket_for_device(dev)

            self._prev_active = set(self.engine.active_devices.keys())

    # =====================================================================
    # 물리 소켓 식별
    # =====================================================================
    def _identify_socket_for_device(self, dev):
        """새 분류된 device 를 PENDING 소켓 중 어느 것에 매핑할지 결정."""
        self._identifying = True
        try:
            candidates = [
                sk for sk in PHYSICAL_SOCKETS
                if self.socket_state[sk] == SOCKET_STATE_PENDING
            ]
            if not candidates:
                # PENDING 없으면 EMPTY 도 보지만 보통 PENDING 이 있을 것
                logging.warning(
                    f"[ORCH] new device {dev}: no PENDING socket; "
                    f"fallback: empty 소켓 찾기"
                )
                candidates = [
                    sk for sk in PHYSICAL_SOCKETS
                    if self.socket_state[sk] in (SOCKET_STATE_EMPTY, SOCKET_STATE_DEVICE_OFF)
                ]

            if not candidates:
                logging.error(
                    f"[ORCH] {dev} 분류됐으나 매핑 가능한 소켓이 없음. 상태: {self._state_summary()}"
                )
                return

            # v62 → v63 → v64: 자동 복원 + 동조율 + 위치 검증.
            # PENDING 후보 중 보존된 라벨이 dev 와 같은 socket 이 있으면:
            #   1) 보존 sig vs 현재 sig 동조율(sim) 계산.
            #      sim < SIM_RESTORE_HIGH 면 "다른 기기" → 보존 데이터 삭제 + break,
            #      아래 일반 분기 (toggle-id) 로 떨어짐 (사용자 "현재 기기 데이터로 등록").
            #   2) sim ≥ SIM_RESTORE_HIGH (또는 보존 sig 없음): 위치 검증 토글 1회.
            #      ΔI ≥ presence 임계 → 진짜 그 socket → auto-restore.
            #      ΔI < 임계 → 그 socket 비어있음 (stale 라벨) → 보존 데이터 삭제 + break
            #      → 일반 toggle-id 가 실제 위치 찾음.
            # 실측 시나리오: S3 보존 라벨=dryer, S4 보존 라벨=cleaner. 사용자가 S4 에
            # 드라이기 새로 꽂음 → AI=dryer → S3 라벨 일치하지만 S3 ΔI≈0 (비어있음)
            # → stale 로 판정, 삭제. toggle-id 로 S4 가 dryer 자리로 발견 (사용자 의도 ✓).
            SIM_RESTORE_HIGH = 0.60
            PRESENCE_RATIO_MIN = 0.5    # ΔI / sig_di 최소 비율
            PRESENCE_ABS_MIN = 1.5      # 절대 최소 (sig_di 가 매우 작을 때 보호)
            VERIFY_N_BEFORE = 4
            VERIFY_N_OFF = 6
            VERIFY_EXCLUDE_FIRST = 1
            VERIFY_N_RESTORE = 2

            for sk in candidates:
                if self.socket_device.get(sk) != dev:
                    continue
                prev_sig = self.socket_device_sig.get(sk)
                cur_sig = {}
                try:
                    cur_sig = self.engine.device_signatures.get(dev, {}) or {}
                except Exception:  # noqa: BLE001
                    pass
                sim = self._signature_similarity(prev_sig, cur_sig)

                # 단계 1: 동조율 낮음 → 보존 데이터 삭제
                if sim is not None and sim < SIM_RESTORE_HIGH:
                    logging.info(
                        f"[ORCH] socket{sk} 보존 dev={dev} sig 동조율 sim={sim:.2f} "
                        f"< {SIM_RESTORE_HIGH:.2f} → 보존 데이터 삭제 후 새로 등록"
                    )
                    self.socket_device[sk] = None
                    self.socket_device_sig[sk] = None
                    break

                # 단계 2: 위치 검증 토글 (v64). 보존 라벨 socket 만 짧게 토글.
                sig_di_for_threshold = abs(float(cur_sig.get("delta_irms", 0.0)))
                presence_threshold = max(
                    sig_di_for_threshold * PRESENCE_RATIO_MIN, PRESENCE_ABS_MIN
                )

                original_cooldown_v64 = int(getattr(self.engine, "event_cooldown", 0))
                try:
                    self._mute_engine(ENGINE_MUTE_FRAMES)
                    i_before_v, _, _ = self._toggle_average_metrics(
                        VERIFY_N_BEFORE, exclude_first=0, label=f"S{sk}-restoreverify-before"
                    )
                    self.relay.set(sk, False)
                    i_off_v, _, _ = self._toggle_average_metrics(
                        VERIFY_N_OFF, exclude_first=VERIFY_EXCLUDE_FIRST,
                        label=f"S{sk}-restoreverify-off"
                    )
                    self.relay.set(sk, True)
                    self._toggle_average_metrics(
                        VERIFY_N_RESTORE, exclude_first=0,
                        label=f"S{sk}-restoreverify-restore"
                    )
                finally:
                    try:
                        self.engine.event_cooldown = max(
                            original_cooldown_v64,
                            int(getattr(self.engine, "event_cooldown", 0)),
                        )
                    except Exception:  # noqa: BLE001
                        pass

                diff_i_v = i_before_v - i_off_v
                sim_text = (
                    f"sim={sim:.2f}" if sim is not None else "sim=N/A(no prev sig)"
                )

                if diff_i_v >= presence_threshold:
                    # 진짜 그 socket → auto-restore + sig refresh
                    logging.info(
                        f"[ORCH][RESTORE-VERIFY] socket{sk} dev={dev} 위치 검증 통과 "
                        f"ΔI={diff_i_v:+.1f} ≥ {presence_threshold:.1f}, {sim_text}"
                    )
                    self._assign(
                        sk, dev,
                        reason=f"auto-restore verified, {sim_text}, ΔI={diff_i_v:+.1f}"
                    )
                    if cur_sig:
                        self.socket_device_sig[sk] = {
                            "delta_irms": float(cur_sig.get("delta_irms", 0.0)),
                            "delta_h1":   float(cur_sig.get("delta_h1", 0.0)),
                            "delta_pabs": float(cur_sig.get("delta_pabs", 0.0)),
                        }
                    return

                # ΔI 임계 미달 → 그 socket 비어있음 (stale 라벨). 삭제 후 일반 분기로.
                logging.info(
                    f"[ORCH][RESTORE-VERIFY] socket{sk} 보존 dev={dev} 위치 검증 실패 "
                    f"ΔI={diff_i_v:+.1f} < {presence_threshold:.1f} → stale 라벨, "
                    f"보존 데이터 삭제 후 일반 toggle-id 로 위치 탐색"
                )
                self.socket_device[sk] = None
                self.socket_device_sig[sk] = None
                break  # 일치 socket 은 dev 당 최대 1개

            if len(candidates) == 1:
                # 토글 식별 불필요. 보존된 다른 라벨은 _assign 에서 dev 로 자동 갱신.
                sk = candidates[0]
                prev = self.socket_device.get(sk)
                reason = "only-candidate"
                if prev is not None and prev != dev:
                    reason = f"only-candidate (replace {prev}→{dev})"
                self._assign(sk, dev, reason=reason)
                return

            # 다중 후보 → 토글로 식별
            chosen = self._toggle_identify(candidates, dev)
            if chosen is not None:
                self._assign(chosen, dev, reason="toggle-id")
            else:
                # 식별 실패: 가장 최근 PENDING (사용자가 마지막에 켠 소켓) 우선
                sk = candidates[-1]
                self._assign(sk, dev, reason="toggle-failed-fallback")
        finally:
            self._identifying = False

    def _signature_similarity(self, prev_sig, cur_sig):
        """두 sig 의 동조율 (0.0 = 완전 다름, 1.0 = 완벽 일치).

        component_sim = min(|a|, |b|) / max(|a|, |b|)  per (delta_irms, delta_h1, delta_pabs)
        전체 similarity = component_sim 평균. 둘 중 하나라도 None/empty 이면 None.

        실측 예 (이번 로그): dryer first dI=648.7 → reclassify dI=749.8
            i_ratio = 648.7/749.8 = 0.87 → "같은 기기" 로 판정 가능.
        """
        if not prev_sig or not cur_sig:
            return None
        keys = ("delta_irms", "delta_h1", "delta_pabs")
        sims = []
        for k in keys:
            try:
                a = abs(float(prev_sig.get(k, 0.0)))
                b = abs(float(cur_sig.get(k, 0.0)))
            except Exception:  # noqa: BLE001
                continue
            if max(a, b) < 1e-3:
                continue  # 둘 다 사실상 0 → 비교 의미 없음, skip
            sims.append(min(a, b) / max(a, b))
        if not sims:
            return None
        return sum(sims) / len(sims)

    def _wait_new_frames(self, n_frames=IDENTIFY_NEW_FRAMES_REQUIRED,
                         max_wait_s=IDENTIFY_MAX_WAIT_S):
        """v37: orchestrator 가 *직접* process_ai_frame 을 호출해 frame 강제 진행.

        실측 (2026-05-22 23:11): 토글 식별 시작 후 matplotlib animation main thread 가
        완전히 stall 되어 _last_ch1 이 모든 토글에서 단 한 번도 갱신 안 됨 (new_frames=False
        x N). main thread 의 frame 도착을 기다리는 polling 방식은 답이 없음.
        engine_lock 으로 SPI race 방지하면서 직접 호출.
        """
        ok_count = 0
        for _ in range(n_frames):
            try:
                with self.engine_lock:
                    self.engine.process_ai_frame()
                ok_count += 1
            except Exception as e:  # noqa: BLE001
                logging.warning(f"[ORCH] direct process_ai_frame failed: {e}")
                break
        return ok_count >= n_frames

    

    def _mute_engine(self, frames):
        """AIEngine 의 event_cooldown 을 강제로 올려서 OFF event 발생 방지."""
        try:
            self.engine.event_cooldown = max(
                int(getattr(self.engine, "event_cooldown", 0)), int(frames)
            )
        except Exception:  # noqa: BLE001
            pass

    def _current_fast_metrics(self):
        """1순위로 가장 최근 프레임의 Irms와 H1을 즉각적으로 가져옵니다."""
        try:
            feats = getattr(self.engine, "frame_feats", None)
            if feats and len(feats) > 0:
                latest = feats[-1]
                # 프레임 단위는 _mean이 없을 수 있으므로 둘 다 체크
                i_val = float(latest.get("Irms_adc", latest.get("Irms_adc_mean", 0.0)))
                h_val = float(latest.get("H1_60_mag", latest.get("H1_60_mag_mean", 0.0)))
                return i_val, h_val
        except Exception:
            pass
        return getattr(self.engine, "baseline_irms", 0.0), 0.0

    def _toggle_average_metrics(self, n_frames, exclude_first=0, label=""):
        """N개 frame 을 process 하고 (Irms, H1) 평균을 반환. 노이즈 평탄화용.

        v56: 단일 frame snapshot 은 cleaner duty cycle 같은 빠른 변동에 극히 취약 (실측
        ±30~40A 변동). LP 디바이스 signal (~2A) 가 노이즈에 묻혀 토글 식별 실패.
        N>=3 frame averaging 으로 duty cycle 일부 cycle 평탄화.

        exclude_first: relay 전이 직후 settling frame 수 (averaging 에서 제외).
        """
        i_samples = []
        h_samples = []
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
            if not feats or len(feats) == 0:
                continue
            try:
                latest = feats[-1]
                i_samples.append(float(latest.get("Irms_adc", 0.0)))
                h_samples.append(float(latest.get("H1_60_mag", 0.0)))
            except Exception:  # noqa: BLE001
                pass
        if not i_samples:
            return 0.0, 0.0, False
        return float(np.mean(i_samples)), float(np.mean(h_samples)), True

    def _toggle_identify(self, candidates, dev):
        """전류(Irms)와 고조파(H1)를 동시에 관측하여 대형 가전의 노이즈를 뚫고 찾아냅니다.

        v56 (2026-05-28 17:49 log 기반):
        - 단일 frame snapshot → multi-frame 평균. cleaner duty noise (±30~40A) 가 TV
          signal (~2A) 을 압도하는 케이스 보정.
        - 양수 후보 0개 일 때 candidates[-1] 임의 fallback (잘못된 socket) 대신 max diff_I
          채택. LP 디바이스 + HP duty noise 환경에서 가장 가능성 큰 socket 보존.

        v57 (2026-05-28 18:17 log 기반):
        - score 공식 `diff_i × 10 + diff_h` 에서 diff_h 가 HP duty 노이즈로 거대 음수가
          나오면 진짜 socket 의 큰 diff_i 양수 signal 을 압도. 실측: TV at S3,
          S3 (diff_I=+38, diff_H1=-7519) 가 S4 (diff_I=+1, diff_H1=+313) 에 score 0역전.
          해결: |diff_h| > 3 × dev sig_dh 시 score 합산에서 0 처리 (HP duty 노이즈로 간주).

        v58 (2026-05-28 18:51 log 기반):
        - presence-ratio 1차 채택. diff_i / sig_di 가 0.5 이상이면 strong 후보로 즉시 채택.
          H1 노이즈 완전 무관, I averaging 기반이라 robust. score 단계 도달 전 빠르게 결정.
          실측: cleaner toggle 시 S2 diff_I=+21.6 (cleaner duty noise) vs S4 diff_I=+120.5
          (실제 cleaner) — sig_di=116.4 기준 presence S2=0.19, S4=1.04 → S4 1차 채택.
        """
        # v56 averaging 파라미터
        TOGGLE_N_BEFORE = 4         # 토글 직전 baseline 측정 frame 수 (~1.6s)
        TOGGLE_N_OFF = 6            # 토글 OFF 상태 측정 frame 수 (~2.4s, cleaner duty 1~2 cycle 커버)
        TOGGLE_EXCLUDE_FIRST = 1    # relay 전이 직후 1 frame 은 settle 중 → 평균에서 제외
        TOGGLE_N_RESTORE = 2        # 측정 끝나고 baseline 회복 frame 수

        original_cooldown = int(getattr(self.engine, "event_cooldown", 0))
        results = {}

        try:
            for sk in candidates:
                self._mute_engine(ENGINE_MUTE_FRAMES)

                i_before, h_before, _ = self._toggle_average_metrics(
                    TOGGLE_N_BEFORE, exclude_first=0, label=f"S{sk}-before"
                )

                self.relay.set(sk, False)
                i_off, h_off, got_new = self._toggle_average_metrics(
                    TOGGLE_N_OFF, exclude_first=TOGGLE_EXCLUDE_FIRST,
                    label=f"S{sk}-off"
                )

                self.relay.set(sk, True)
                self._toggle_average_metrics(
                    TOGGLE_N_RESTORE, exclude_first=0, label=f"S{sk}-restore"
                )

                diff_i = i_before - i_off
                diff_h = h_before - h_off
                results[sk] = (i_before, i_off, diff_i, diff_h, got_new)

                logging.info(
                    f"[ORCH][TOGGLE-ID] dev={dev} socket{sk}: "
                    f"diff_I={diff_i:+.1f}, diff_H1={diff_h:+.1f}, "
                    f"i_b_avg={i_before:.1f}, i_off_avg={i_off:.1f} "
                    f"(n_b={TOGGLE_N_BEFORE}, n_off={TOGGLE_N_OFF - TOGGLE_EXCLUDE_FIRST})"
                )

            # v58: presence-ratio 1차 채택. diff_i 를 dev 의 sig_di 로 정규화.
            # 실제 dev 가 있는 socket 은 presence ≈ 1.0, 빈 자리는 ≈ 0. H1 노이즈 무관.
            # 실측 (이번 18:52:29 cleaner): S2 diff_I=+21.6 (cleaner duty noise 우연 일치)
            #   vs S4 diff_I=+120.5 (실제 cleaner). sig_di=116.4 → S2 presence=0.19,
            #   S4 presence=1.04 → S4 즉시 채택. score 단계로 안 내려가서 H1 노이즈 영향 0.
            PRESENCE_STRONG_THRESHOLD = 0.5
            PRESENCE_AMBIG_RATIO = 0.8  # 1위 대비 2위 비율 ≥ 0.8 이면 모호 → score fallback
            try:
                sig_di_dev = abs(float(
                    self.engine.device_signatures.get(dev, {}).get("delta_irms", 0.0)
                ))
            except Exception:  # noqa: BLE001
                sig_di_dev = 0.0

            if sig_di_dev > 0.5:
                strong = []
                for sk, res in results.items():
                    diff_i = res[2]
                    if diff_i <= 0:
                        continue
                    presence = diff_i / sig_di_dev
                    if presence >= PRESENCE_STRONG_THRESHOLD:
                        strong.append((sk, presence, diff_i, res[3]))
                strong.sort(key=lambda x: -x[1])
                if strong:
                    best_sk_p, best_p, b_di, b_dh = strong[0]
                    if (len(strong) >= 2
                            and strong[1][1] >= PRESENCE_AMBIG_RATIO * best_p):
                        logging.info(
                            f"[ORCH][TOGGLE-ID] {dev} presence 1·2위 근접 "
                            f"(S{best_sk_p}={best_p:.2f} vs S{strong[1][0]}={strong[1][1]:.2f}) "
                            f"→ score fallback 으로 검증"
                        )
                        # fall through to score-based 로직
                    else:
                        logging.info(
                            f"[ORCH][TOGGLE-ID] {dev} presence-strong 채택: "
                            f"socket{best_sk_p} (presence={best_p:.2f}, "
                            f"sig_di={sig_di_dev:.1f}, diff_I={b_di:+.1f}, "
                            f"diff_H1={b_dh:+.1f})"
                        )
                        return best_sk_p

            # v57: diff_h clipping 을 위한 dev sig_dh.
            # cleaner 같은 HP duty 디바이스는 H1 가 ±5000~10000 변동. 한 후보의 diff_h 가
            # 노이즈 swing 에 걸리면 -7519 같은 거대 음수가 나와 score 를 망가뜨림.
            # 실측 (2026-05-28 18:18:36): TV at S3, cleaner active 중:
            #   S3 (실제 TV): diff_I=+38, diff_H1=-7519 → score = 380 + (-7519) = -7139
            #   S4 (빈 자리): diff_I=+1, diff_H1=+313  → score = 10 + 313       = +323
            # diff_I 는 S3 이 명확한 1위인데 H1 노이즈가 score 결정을 뒤집어 S4 잘못 선택.
            # 해결: |diff_h| 가 dev sig_dh 의 H_CLIP_MULTIPLIER 배 초과면 노이즈로 간주, 0 처리.
            # → 위 case: TV sig_dh=1435, 임계=4305. S3 |-7519|>4305 → clip to 0 → score=380.
            #   S4 |313|<4305 → score=323. S3 wins ✓
            H_CLIP_MULTIPLIER = 3.0
            try:
                sig_dh_dev = abs(float(
                    self.engine.device_signatures.get(dev, {}).get("delta_h1", 0.0)
                ))
            except Exception:  # noqa: BLE001
                sig_dh_dev = 0.0
            h_clip_threshold = (
                H_CLIP_MULTIPLIER * sig_dh_dev if sig_dh_dev > 50.0 else float("inf")
            )

            def _clip_h(d_h):
                """sig_dh 의 H_CLIP_MULTIPLIER 배 초과 절댓값은 HP duty 노이즈로 보고 0 처리.
                sig_dh 가 너무 작거나 (50 미만 → 등록 직후, 신뢰 어려움) None 이면 clip 안 함."""
                if abs(d_h) > h_clip_threshold:
                    return 0.0, True
                return d_h, False

            # Irms 가중치(x10)와 H1 감소량을 합산해 진짜 스위치를 찾아냄
            positive = []
            for sk, res in results.items():
                diff_i = res[2]
                diff_h_raw = res[3]
                # v48: sign-inconsistency 필터. diff_i 가 명확히 음수 (-1.5 미만) 이면
                # relay OFF 했는데 I 가 *증가* 한 것 → toggle 결과가 아니라 다른 active
                # 가전 (cleaner motor 등) 의 duty-cycle 변동이 우연히 측정 시점에 겹친 것.
                # diff_H 가 양수더라도 그 변화도 노이즈일 가능성 → 후보 제외.
                # 실측 (2026-05-25 01:01:42): cleaner active 중 charger 토글 식별에서
                # socket1 diff_I=-10.5, diff_H1=+2730.9 (cleaner 변동) 가 실제 charger
                # socket3 diff_I=+20.2, diff_H1=+851.3 보다 큰 score 로 잘못 선택됨.
                if diff_i < -1.5:
                    logging.info(
                        f"[ORCH][TOGGLE-ID-SKIP] socket{sk} diff_I={diff_i:+.1f} 음수 → "
                        f"다른 가전 noise 가능성, 후보 제외"
                    )
                    continue

                diff_h_eff, clipped = _clip_h(diff_h_raw)
                if clipped:
                    logging.info(
                        f"[ORCH][TOGGLE-ID-HCLIP] socket{sk} diff_H1={diff_h_raw:+.1f} "
                        f"|.|>{h_clip_threshold:.0f} (3×sig_dh={sig_dh_dev:.0f}) → "
                        f"HP duty 노이즈로 간주, score 에서 0 처리"
                    )

                # 충전기 같은 미세 전력 기기는 H1 감소(50 이상)가 핵심 단서임
                if diff_i > 1.5 or diff_h_eff > 50.0:
                    score = (diff_i * 10.0) + diff_h_eff
                    positive.append((sk, score, diff_i, diff_h_raw))

            positive.sort(key=lambda x: -x[1])

            # v56: 양수 후보 있고 명확한 1위면 채택. 모호하면 relax-fallback 로 떨어짐.
            if positive:
                best_socket, best_score, b_diff_i, b_diff_h = positive[0]
                if len(positive) >= 2:
                    second_sk, second_score, _, _ = positive[1]
                    if second_score > 0 and best_score < second_score * 1.3:
                        logging.warning(
                            f"[ORCH][TOGGLE-ID] {dev} 식별 모호 "
                            f"(best S{best_socket}={best_score:.1f} vs "
                            f"second S{second_sk}={second_score:.1f}) → relax-fallback"
                        )
                        # fall through 해서 아래 max-diff_I 로 결정
                    else:
                        return best_socket
                else:
                    return best_socket

            # v56: relax-fallback. 양수 후보 없거나 모호일 때 candidates[-1] 임의 채택 대신
            # results 중 max diff_I 채택. LP 디바이스 + HP duty noise 환경 안전.
            # 실측 (2026-05-28 17:50:55): TV at S2, cleaner active:
            #   S2 diff_I=+0.3 (TV 의 미세 signal), S4 diff_I=-38.5 (cleaner duty 노이즈)
            #   기존: candidates[-1] = S4 (wrong)
            #   v56: max diff_I = S2 (correct, TV 의 작은 양수 signal 채택)
            if results:
                best_sk, best_res = max(results.items(), key=lambda kv: kv[1][2])
                b_diff_i, b_diff_h = best_res[2], best_res[3]

                # 모든 후보가 명확히 음수 (-5 이하) → 진짜 식별 불가, None 반환 (외부 fallback)
                if b_diff_i < -5.0:
                    logging.warning(
                        f"[ORCH][TOGGLE-ID] {dev} 모든 후보 음수 diff (max={b_diff_i:+.1f}) → "
                        f"식별 실패; results={results}"
                    )
                    return None

                logging.info(
                    f"[ORCH][TOGGLE-ID] {dev} relax-fallback (max diff_I): socket{best_sk} "
                    f"diff_I={b_diff_i:+.1f}, diff_H1={b_diff_h:+.1f}; results={results}"
                )
                return best_sk

            logging.warning(f"[ORCH][TOGGLE-ID] {dev} 측정 실패; results={results}")
            return None
        finally:
            try:
                self.engine.event_cooldown = max(
                    original_cooldown, int(getattr(self.engine, "event_cooldown", 0))
                )
            except Exception:
                pass

    # =====================================================================
    # 매핑/OFF 처리
    # =====================================================================
    def _assign(self, sk, dev, reason="?"):
        # v77: 한 dev = 한 socket 원칙. 다른 socket 에 같은 dev 라벨이 보존돼 있으면
        # 정리. 사용자 시나리오 (실측): S4=DEVICE_OFF(dryer 보존) + 사용자가 S2 에 새로
        # dryer 꽂음 → S2 매핑 진행. dryer 가 S2 에 들어왔다는 건 S4 에서 빠진 것 →
        # S4 의 stale 라벨/sig 정리해서 EMPTY 로. 향후 매핑 충돌 방지.
        for other_sk in PHYSICAL_SOCKETS:
            if other_sk == sk:
                continue
            if self.socket_device.get(other_sk) == dev:
                old_state = self.socket_state.get(other_sk)
                self.socket_device[other_sk] = None
                self.socket_device_sig[other_sk] = None
                # ASSIGNED 였으면 기존 _assign 흐름상 모순이지만 안전을 위해 처리.
                # DEVICE_OFF 였으면 EMPTY 로. PENDING (희박) 도 EMPTY 로.
                self.socket_state[other_sk] = SOCKET_STATE_EMPTY
                logging.info(
                    f"[ORCH] socket{other_sk} 의 stale {dev} 라벨 정리 ({old_state} "
                    f"→ EMPTY), socket{sk} 새 매핑으로 dev 이동 추정"
                )

        self.socket_state[sk] = SOCKET_STATE_ASSIGNED
        self.socket_device[sk] = dev
        self.last_event = f"assigned {dev} → socket{sk} ({reason})"
        logging.info(f"[ORCH] {self.last_event}")

    # =====================================================================
    # OFF verify callback (v53: 토글 검증)
    # =====================================================================
    def _measure_irms_h1_raw(self):
        """SPI raw 모드로 직접 측정한 즉시 Irms (ADC).

        AIEngine 이 DSPEngine 을 상속하므로 self.engine.process_raw_mode() 직접 호출 가능.
        process_ai_frame 을 호출하면 frame_count/baseline EMA/이벤트 분류까지 다 돌아서
        callback 안 재진입 시 부수효과 누적. raw 만 가져와서 RMS 계산.
        """
        i_rms, _ = self._measure_irms_and_h1_raw()
        return i_rms

    def _measure_irms_and_h1_raw(self):
        """SPI raw 모드로 즉시 (Irms, H1_60_mag) 동시 측정.

        v80: 작은 LP (tv/charger) 를 큰 HP (dryer/cleaner) 와 동시에 켠 상태에서
        토글 검증할 때, Irms 단독은 SNR 이 너무 나쁘다 — 전체 RMS 가 ~900 인데
        HP duty-cycle 노이즈 std 가 ±15 라, tv 의 sig_di≈34 와 같은 크기여서
        "부하 잔존(ΔI≈sig)" 과 "노이즈" 가 구분 불가 (실측 2026-05-30 21:38:04
        tv@S4 ΔI=+33.8 ratio=1.00 std=15.5 — 사용자가 TV 를 이미 뽑았는데도 노이즈가
        sig 방향으로 찍혀 "잔존" 오판). H1(60Hz bin)은 LP 의 위상 부하를 직접 잡아
        tv sig_h1≈1822 처럼 노이즈 대비 압도적으로 커서 SNR 이 좋다.
        feature_extractor._compute_harmonics 를 재사용해 학습/추론과 동일한 H1 정의 유지.
        """
        try:
            with self.engine_lock:
                ch0, ch1, ts, fs = self.engine.process_raw_mode()
            ch1_arr = np.asarray(ch1, dtype=np.float64)
            i_rms = float(np.sqrt(np.mean(ch1_arr ** 2)))
            h1 = None
            try:
                from feature_extractor import _compute_harmonics
                harm = _compute_harmonics(ch1_arr, fs)
                h1 = float(harm.get("H1_60_mag", 0.0))
            except Exception:  # noqa: BLE001
                h1 = None
            return i_rms, h1
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[ORCH][OFF-VERIFY] raw Irms/H1 measure failed: {e}")
            return None, None

    # =====================================================================
    # v2: OFF 전수 스캔 (signature 추측 없이 릴레이 토글로 물리 확정)
    # =====================================================================
    def _sig_h1_for(self, sk):
        dev = self.socket_device.get(sk)
        if dev is None:
            return 0.0
        return abs(float(self.engine.device_signatures.get(dev, {}).get("delta_h1", 0.0)))

    def _check_off_suspect(self):
        """AIEngine 이 off_suspect 를 세우면 ASSIGNED 소켓 전수 스캔으로 OFF 확정."""
        if not getattr(self.engine, "off_suspect", False):
            return
        with self.lock:
            self._identifying = True
            any_off = False
            any_disturbed = False
            try:
                any_off, any_disturbed = self._full_scan_off()
            finally:
                self._identifying = False
                try:
                    self.engine.off_suspect = False
                    self.engine._off_suspect_consec = 0
                    if not any_off:
                        if any_disturbed:
                            # 측정 교란으로 진짜 부재 기기를 놓쳤을 수 있다. baseline 은
                            # 그대로 두어(하락 유지) 다음 frame 에서 재트리거 → 재스캔으로
                            # 정확히 잡게 한다. 짧은 cooldown 으로 즉시 연타만 방지.
                            self.engine.event_cooldown = max(
                                int(getattr(self.engine, "event_cooldown", 0)),
                                ENGINE_MUTE_FRAMES,
                            )
                            logging.info(
                                "[ORCH][OFF-SCAN] 교란 있었음 → baseline 유지, 곧 재스캔"
                            )
                        else:
                            # 순수 false positive (전부 또렷이 잔존): H1 dip 노이즈였다.
                            # baseline 을 현재값으로 sync 해 하락을 흡수, 무한 루프 차단.
                            wf = getattr(self.engine, "_latest_win_feat", None)
                            if wf and hasattr(self.engine, "_sync_baseline_to"):
                                self.engine._sync_baseline_to(wf)
                            self.engine.event_cooldown = max(
                                int(getattr(self.engine, "event_cooldown", 0)),
                                ENGINE_MUTE_FRAMES,
                            )
                except Exception:  # noqa: BLE001
                    pass

    def _full_scan_off(self):
        """ASSIGNED 소켓을 작은 sig(LP) 우선으로 하나씩 토글해 부재 기기 확정.

        shortfall(사라진 H1 추정량) 이 확정된 OFF 기기들로 설명되면 조기 종료.
        """
        assigned = [
            sk for sk in PHYSICAL_SOCKETS
            if self.socket_state[sk] == SOCKET_STATE_ASSIGNED
            and self.socket_device.get(sk) is not None
        ]
        if not assigned:
            logging.info("[ORCH][OFF-SCAN] ASSIGNED 소켓 없음 → skip")
            return

        # LP(작은 sig) 우선: 작은 변화부터 확정해 큰 HP 노이즈에 묻히는 LP 를 먼저 구제.
        order = sorted(assigned, key=self._sig_h1_for)
        remaining = float(getattr(self.engine, "off_suspect_drop_h1", 0.0))
        logging.info(
            f"[ORCH][OFF-SCAN] 시작 targets={[(sk, self.socket_device[sk]) for sk in order]} "
            f"shortfall={remaining:.1f}"
        )
        self._mute_engine(ENGINE_MUTE_FRAMES * 2)

        any_off = False
        any_disturbed = False
        for sk in order:
            dev = self.socket_device[sk]
            sig_h1_dev = self._sig_h1_for_dev(dev)   # _finalize_off 가 sig 를 pop 하기 전에 저장
            verdict, drop_h1, disturbed = self._scan_one_socket(sk)
            any_disturbed = any_disturbed or disturbed
            if verdict == "absent":
                self._finalize_off(sk)
                any_off = True
                remaining -= sig_h1_dev
                if remaining <= OFF_SCAN_REMAIN_STOP:
                    logging.info(
                        f"[ORCH][OFF-SCAN] shortfall 잔량={remaining:.1f} ≤ "
                        f"{OFF_SCAN_REMAIN_STOP} → 조기 종료"
                    )
                    break

        if not any_off:
            logging.info(
                f"[ORCH][OFF-SCAN] 부재 소켓 없음 (전부 잔존, 교란={any_disturbed})"
            )
        return any_off, any_disturbed

    def _sig_h1_for_dev(self, dev):
        return abs(float(self.engine.device_signatures.get(dev, {}).get("delta_h1", 0.0)))

    def _scan_one_socket(self, sk):
        """소켓 sk 를 짧게 relay OFF → ΔH1 측정 → ('absent'|'present', drop_h1).

        부재(이미 빠짐): relay OFF 해도 H1 거의 안 빠짐 → ratio_h1 ≈ 0.
        잔존(살아있음): relay OFF 에 H1 이 sig 만큼 빠짐 → ratio_h1 ≈ 1.
        """
        dev = self.socket_device[sk]
        sig_dh1 = self._sig_h1_for_dev(dev)
        sig_di = abs(float(self.engine.device_signatures.get(dev, {}).get("delta_irms", 0.0)))

        self._mute_engine(ENGINE_MUTE_FRAMES)
        i_before, h1_before, _ = self._toggle_average_metrics(
            SCAN_N_BEFORE, exclude_first=0, label=f"S{sk}-scan-before"
        )
        self.relay.set(sk, False)
        time.sleep(OFF_VERIFY_SETTLE_S)
        i_off, h1_off, _ = self._toggle_average_metrics(
            SCAN_N_OFF, exclude_first=SCAN_EXCLUDE_FIRST, label=f"S{sk}-scan-off"
        )
        self.relay.set(sk, True)               # 일단 복원 (부재 확정 시 _finalize_off 가 다시 OFF)
        time.sleep(OFF_VERIFY_SETTLE_S)
        self._toggle_average_metrics(SCAN_N_RESTORE, exclude_first=0, label=f"S{sk}-scan-restore")

        diff_h1 = h1_before - h1_off
        diff_i = i_before - i_off

        # sig_dh1 신뢰 가능 → H1 ratio 우선 (SNR 압도적)
        if sig_dh1 > MIN_SIG_H1:
            ratio_h1 = diff_h1 / sig_dh1
            # 판정 (양방향):
            #   absent (이미 빠짐): relay OFF 해도 H1 거의 안 빠짐 → ratio ≈ 0 → |ratio| < 0.30
            #   present (살아있음): relay OFF 에 H1 이 sig 만큼 빠짐 → ratio ≈ +1 → ratio ≥ 0.30
            #   |ratio| ≥ 0.30 인데 음수: relay OFF 했는데 H1 이 *상승* = 측정 교란.
            #     작은 LP(charger) 소켓 토글이 같은 계통의 큰 HP(dryer) H1 을 출렁이게 해
            #     ΔH1 이 ±수천으로 요동 (실측 2026-05-31 03:10~11: charger@S3 가 살아있든
            #     죽었든 ΔH1=-5473/-6589 교란, sig 540 의 10배). 이 경우 H1 판정 불가.
            #
            # v2.1: H1 교란 시 ΔI 보조 판정. 실측에서 ΔI 는 깨끗했다:
            #   charger 살아있음 → ΔI≈+27 (그 소켓 끄면 전류 빠짐)
            #   charger 부재     → ΔI≈0  (이미 없어 안 빠짐)
            # sig_di 정보로 ratio_i 를 만들어 0 근처면 absent, 큰 양수면 present.
            if abs(ratio_h1) < OFF_CONFIRM_RATIO:
                # H1 으로 또렷이 판정 가능 (교란 없음)
                logging.info(
                    f"[ORCH][OFF-SCAN] {dev}@S{sk}: ΔH1={diff_h1:+.0f}, sig_dh1={sig_dh1:.0f}, "
                    f"ratio_h1={ratio_h1:.2f}, ΔI={diff_i:+.1f} → absent"
                )
                return "absent", diff_h1, False
            if ratio_h1 >= OFF_CONFIRM_RATIO:
                # H1 이 sig 방향으로 또렷이 빠짐 = 확실히 살아있음
                logging.info(
                    f"[ORCH][OFF-SCAN] {dev}@S{sk}: ΔH1={diff_h1:+.0f}, sig_dh1={sig_dh1:.0f}, "
                    f"ratio_h1={ratio_h1:.2f}, ΔI={diff_i:+.1f} → present"
                )
                return "present", diff_h1, False

            # ratio_h1 ≤ -0.30: H1 측정 교란 → ΔI 보조 판정
            verdict, by = self._verdict_by_irms(diff_i, sig_di)
            logging.info(
                f"[ORCH][OFF-SCAN] {dev}@S{sk}: ΔH1={diff_h1:+.0f} (ratio_h1={ratio_h1:.2f}, "
                f"H1 교란) → ΔI={diff_i:+.1f}/sig_di={sig_di:.0f} 보조판정 → {verdict} ({by})"
            )
            # ΔI 로도 명확히 못 가르면(ambiguous) 교란으로 표시해 재스캔 위임
            return verdict, diff_h1, (by == "ambiguous")

        # sig_dh1 신뢰 불가 → Irms 절대 임계 fallback (|ΔI| 작으면 부재)
        verdict = "absent" if abs(diff_i) < OFF_VERIFY_MIN_DELTA_I else "present"
        logging.info(
            f"[ORCH][OFF-SCAN] {dev}@S{sk}: sig_dh1={sig_dh1:.0f}<{MIN_SIG_H1} → Irms fallback "
            f"ΔI={diff_i:+.1f} (임계 ±{OFF_VERIFY_MIN_DELTA_I}) → {verdict}"
        )
        return verdict, diff_h1, False

    def _verdict_by_irms(self, diff_i, sig_di):
        """H1 교란 시 ΔI 로 부재/잔존 보조 판정.

        살아있는 소켓을 끄면 ΔI ≈ +sig_di (전류 빠짐), 부재면 ΔI ≈ 0.
        반환: (verdict, reason). reason='ambiguous' 면 ΔI 로도 불확실 → 재스캔 권장.
        """
        # 절대 하한: sig_di 가 작아도(charger~17) 최소 이만큼은 빠져야 present.
        present_thresh = max(OFF_VERIFY_MIN_DELTA_I, sig_di * OFF_SCAN_IRMS_PRESENT_RATIO)
        absent_thresh = max(OFF_VERIFY_MIN_DELTA_I * 0.6, sig_di * OFF_SCAN_IRMS_ABSENT_RATIO)
        if diff_i >= present_thresh:
            return "present", "ΔI 큼=잔존"
        if diff_i < absent_thresh:
            return "absent", "ΔI 0근처=부재"
        return "present", "ambiguous"  # 중간: 보수적으로 present(잘못 OFF 방지) + 재스캔

    def _finalize_off(self, sk):
        """부재 확정 소켓: relay OFF 유지 + DEVICE_OFF state + engine.confirm_device_off."""
        dev = self.socket_device[sk]
        # OFF 직전 sig snapshot (재ON 자동복원 비교용)
        try:
            sig = self.engine.device_signatures.get(dev, {})
            if sig:
                self.socket_device_sig[sk] = {
                    "delta_irms": float(sig.get("delta_irms", 0.0)),
                    "delta_h1":   float(sig.get("delta_h1", 0.0)),
                    "delta_pabs": float(sig.get("delta_pabs", 0.0)),
                }
        except Exception:  # noqa: BLE001
            pass

        try:
            self.relay.set(sk, False)
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[ORCH] relay.set({sk},False) failed: {e}")
        self.socket_state[sk] = SOCKET_STATE_DEVICE_OFF

        try:
            self.engine.confirm_device_off(dev)
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[ORCH] engine.confirm_device_off({dev}) failed: {e}")

        if dev in HIGH_POWER_DEVICES:
            self._last_hp_off_t = time.perf_counter()
        # _prev_active 동기화 (confirm_device_off 로 빠진 dev 가 removed 로 안 잡히게)
        self._prev_active.discard(dev)
        self.last_event = f"{dev} OFF (full-scan) → socket{sk} relay OFF (standby cut)"
        logging.info(f"[ORCH] {self.last_event}")

    # 상태 조회 / 디버그
    # =====================================================================
    def get_socket_status(self):
        """UI 용 dict: {socket_idx: {state, device}, ...}."""
        with self.lock:
            return {
                sk: {
                    "state": self.socket_state[sk],
                    "device": self.socket_device[sk],
                }
                for sk in PHYSICAL_SOCKETS
            }

    def _state_summary(self):
        return ", ".join(
            f"S{sk}:{self.socket_state[sk]}"
            + (f"({self.socket_device[sk]})" if self.socket_device[sk] else "")
            for sk in PHYSICAL_SOCKETS
        )


# =====================================================================
# CLI 자가 테스트 (Mock) — v2 전수 스캔 OFF 판정 검증
# =====================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    class MockRelay:
        def __init__(self):
            self.state = {1: False, 2: False, 3: False, 4: False}
        def set(self, idx, on):
            self.state[idx] = on
        def all_off(self):
            for k in self.state:
                self.state[k] = False
        def get_state(self):
            return dict(self.state)

    # Mock AIEngine: process_ai_frame 이 frame_feats 에 현재 H1 을 넣는다.
    # 각 소켓의 relay 상태에 따라 H1 합산을 시뮬 (켜진 기기만 H1 기여).
    class MockEngine:
        DEV_H1 = {"dryer": 18000.0, "cleaner": 6500.0, "charger": 650.0, "tv": 1400.0}
        DEV_I  = {"dryer": 370.0, "cleaner": 120.0, "charger": 20.0, "tv": 34.0}

        def __init__(self, relay):
            self.relay = relay
            self.active_devices = {}      # dev -> socket idx
            self.device_signatures = {}   # dev -> {delta_h1, delta_irms}
            self.baseline_irms = 80.0
            self.baseline_h1 = 80.0
            self.idle_baseline_h1 = 80.0
            self.event_cooldown = 0
            self.off_suspect = False
            self.off_suspect_drop_h1 = 0.0
            self._off_suspect_consec = 0
            self.frame_feats = []
            self._latest_win_feat = {}
            self.unplugged = set()        # 사용자가 물리적으로 뽑은 기기 (relay 무관 H1 기여 0)
            self.inject_h1 = 0.0          # 측정 교란 시뮬: 매 frame H1 에 더해질 노이즈

        def _cur_h1_i(self):
            h1 = self.idle_baseline_h1 + self.inject_h1
            i = self.baseline_irms
            for dev, sk in self.active_devices.items():
                if dev in self.unplugged:
                    continue
                if not self.relay.get_state().get(sk, False):
                    continue  # relay OFF → H1 기여 0
                h1 += self.DEV_H1.get(dev, 0.0)
                i += self.DEV_I.get(dev, 0.0)
            return h1, i

        def process_ai_frame(self):
            h1, i = self._cur_h1_i()
            self.frame_feats = [{"Irms_adc": i, "H1_60_mag": h1}]
            self._latest_win_feat = {"Irms_adc_mean": i, "H1_60_mag_mean": h1}
            return {"win_feat": self._latest_win_feat}

        def process_raw_mode(self):
            import numpy as _np
            h1, i = self._cur_h1_i()
            return _np.zeros(150), _np.full(150, i), _np.zeros(150), 1900.0

        def confirm_device_off(self, dev, win_feat=None):
            self.device_signatures.pop(dev, None)
            self.active_devices.pop(dev, None)
            h1, i = self._cur_h1_i()
            self.baseline_h1 = h1
            self.baseline_irms = i
            self.off_suspect = False
            self._off_suspect_consec = 0
            print(f"  [MOCK ENGINE] confirm_device_off({dev}) → active={list(self.active_devices)}")

        def _sync_baseline_to(self, win_feat):
            self.baseline_h1 = float(win_feat.get("H1_60_mag_mean", self.baseline_h1))
            self.baseline_irms = float(win_feat.get("Irms_adc_mean", self.baseline_irms))

    relay = MockRelay()
    engine = MockEngine(relay)
    orch = SocketOrchestrator(relay_controller=relay, ai_engine=engine)

    # 시나리오: dryer/cleaner/charger 가 동시 ON (각 소켓 ASSIGNED), 사용자가 charger 를 뽑음.
    for sk, dev in [(1, "dryer"), (2, "cleaner"), (3, "charger")]:
        relay.set(sk, True)
        orch.socket_state[sk] = SOCKET_STATE_ASSIGNED
        orch.socket_device[sk] = dev
        engine.active_devices[dev] = sk
        engine.device_signatures[dev] = {
            "delta_h1": MockEngine.DEV_H1[dev], "delta_irms": MockEngine.DEV_I[dev],
        }
    orch._prev_active = set(engine.active_devices)
    engine.baseline_h1, engine.baseline_irms = engine._cur_h1_i()  # 3기기 ON 안정 baseline

    print("\n=== 케이스 A: charger 뽑힘 → charger 만 OFF ===")
    engine.unplugged.add("charger")          # relay 는 ON 이지만 H1 기여 0 (뽑힘)
    engine.off_suspect = True
    engine.off_suspect_drop_h1 = MockEngine.DEV_H1["charger"]
    orch._check_off_suspect()
    print(f"  active={list(engine.active_devices)}, S3={orch.socket_state[3]}")
    assert "charger" not in engine.active_devices, "charger 가 OFF 처리되지 않음!"
    assert orch.socket_state[3] == SOCKET_STATE_DEVICE_OFF, "socket3 state 가 DEVICE_OFF 아님!"
    assert "dryer" in engine.active_devices and "cleaner" in engine.active_devices, "HP 가 잘못 OFF 됨!"
    print("  ✅ charger 만 OFF, dryer/cleaner 유지")

    print("\n=== 케이스 B: false positive (아무도 안 뽑힘) → 아무도 OFF 안 됨 + baseline sync ===")
    engine.off_suspect = True
    engine.off_suspect_drop_h1 = 500.0       # H1 dip 처럼 보이지만 실제론 다 살아있음
    before = set(engine.active_devices)
    orch._check_off_suspect()
    assert set(engine.active_devices) == before, "false positive 인데 기기가 OFF 됨!"
    assert engine.event_cooldown >= 1, "false positive 후 cooldown 안 걸림 (무한 루프 위험)!"
    print(f"  ✅ active 그대로={list(engine.active_devices)}, cooldown={engine.event_cooldown} (루프 방지)")

    # 케이스 C: 이번 실측 버그 재현 — dryer/cleaner/charger/tv 다 ON, tv 를 뽑았는데
    # 첫 스캔 소켓(charger, 작은 sig)에서 측정 교란(거대 음수 ΔH1)이 나는 상황.
    # 기존 버그: charger 가 absent 오판 → charger 잘못 OFF (한 칸 밀림).
    # 수정 후: charger 는 present(교란), tv 가 absent 로 정확히 잡혀야 함.
    print("\n=== 케이스 C: tv 뽑힘 + charger 소켓 측정 교란 → tv 만 OFF (한 칸 밀림 방지) ===")
    relay2 = MockRelay(); engine2 = MockEngine(relay2)
    orch2 = SocketOrchestrator(relay_controller=relay2, ai_engine=engine2)
    for sk, dev in [(1, "dryer"), (2, "cleaner"), (3, "charger"), (4, "tv")]:
        relay2.set(sk, True); orch2.socket_state[sk] = SOCKET_STATE_ASSIGNED
        orch2.socket_device[sk] = dev; engine2.active_devices[dev] = sk
        engine2.device_signatures[dev] = {
            "delta_h1": MockEngine.DEV_H1[dev], "delta_irms": MockEngine.DEV_I[dev],
        }
    orch2._prev_active = set(engine2.active_devices)
    engine2.baseline_h1, engine2.baseline_irms = engine2._cur_h1_i()

    # tv 를 물리적으로 뽑음. 동시에 charger 스캔 구간에 거대 H1 상승 교란 주입.
    engine2.unplugged.add("tv")
    # _scan_one_socket 을 wrap 해서 charger(S3) 스캔 동안만 inject_h1 을 큰 값으로.
    _orig_scan = orch2._scan_one_socket
    def _scan_with_noise(sk):
        engine2.inject_h1 = 5000.0 if sk == 3 else 0.0   # charger 소켓만 교란
        try:
            return _orig_scan(sk)
        finally:
            engine2.inject_h1 = 0.0
    orch2._scan_one_socket = _scan_with_noise

    engine2.off_suspect = True
    engine2.off_suspect_drop_h1 = MockEngine.DEV_H1["tv"]
    orch2._check_off_suspect()
    print(f"  active={list(engine2.active_devices)}, S4(tv)={orch2.socket_state[4]}, S3(charger)={orch2.socket_state[3]}")
    assert "tv" not in engine2.active_devices, "FAIL: tv 가 OFF 안 됨!"
    assert "charger" in engine2.active_devices, "FAIL: charger 가 교란으로 잘못 OFF 됨 (한 칸 밀림)!"
    assert {"dryer", "cleaner"} <= set(engine2.active_devices), "FAIL: HP 잘못 OFF!"
    print("  ✅ tv 만 OFF, charger(교란)/dryer/cleaner 유지 — 한 칸 밀림 해결")

    print("\n✅ ALL PASS")
