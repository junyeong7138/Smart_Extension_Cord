#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
socket_dashboard.py
===================
*물리* socket 1~4 의 상태를 표시하는 matplotlib UI.

진실 소스는 SocketOrchestrator 의 매핑이다 (orchestrator.get_socket_status()).
AIEngine 의 내부 가상 socket 매핑은 *사용하지 않는다*.

레이아웃 (v3 의 AIDashboardUI 와 유사):
    상단 : Socket 1~4 카드 (state, device, power)
    중단 : Oscilloscope (CH0 voltage, CH1 current — dashboard_ui 와 동일 스타일)
    하단 : info text (frame, fs, baseline, current, delta, active devices)
    최하단 : 제어 버튼 패널 (mobile_ui 와 동일 기능 — 소켓별 ON/OFF 토글·재스캔, 모두 OFF)

제어 패널 (mobile_ui.py 의 버튼과 1:1 대응)
------------------------------------------
- 소켓별 ON/OFF 토글  : relay.toggle(sk) + orchestrator.on_external_relay_change(sk)
- 소켓별 재스캔        : orchestrator.rescan_socket(sk) (수동 재추론)
- 모두 OFF            : 각 소켓 relay.set(sk, False) + 동기화
- 새로고침            : 애니메이션이 100ms 마다 자동 갱신 (mobile 의 2초 자동 새로고침 대응)

⚠️ 기존 분류/매핑/OFF 로직은 손대지 않는다. 버튼은 orchestrator/relay 의 *기존 public
메서드*만 호출한다. rescan_socket 은 수 초 블로킹이므로 (mobile 이 Flask 워커 스레드에서
돌리는 것과 동일하게) 백그라운드 daemon thread 에서 실행하고, busy 가드 + 상태 토스트로
matplotlib 메인 스레드(애니메이션)가 멈추지 않게 한다.
"""

import logging
import threading
import time

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button


# Device → 표시용 전력 (UI 에만 사용)
DEVICE_POWER_W = {
    "charger": 5,
    "tv": 60,
    "cleaner": 600,
    "microwave": 900,
    "dryer": 1800,
}

N_PHYS_SOCKETS = 4


class SocketDashboard:
    """SocketOrchestrator + AIEngine + (optional) DashboardUI 연동 matplotlib UI."""

    COLOR_EMPTY = "#404040"
    COLOR_PENDING = "#1976D2"
    COLOR_ASSIGNED = "#00C853"
    COLOR_DEVICE_OFF = "#FF8C00"

    BORDER_EMPTY = "#888888"
    BORDER_PENDING = "#42A5F5"
    BORDER_ASSIGNED = "#00FF00"
    BORDER_DEVICE_OFF = "#FFA500"

    STATE_LABEL = {
        "EMPTY": ("EMPTY", "white"),
        "PENDING": ("PENDING", "white"),
        "ASSIGNED": ("ON", "white"),
        "DEVICE_OFF": ("OFF", "white"),
    }

    def __init__(self, engine, orchestrator):
        self.engine = engine
        self.orchestrator = orchestrator
        self.buffer_size = getattr(engine, "buffer_size", 150)

        # =====================================================
        # Figure / Grid
        # =====================================================
        self.fig = plt.figure(figsize=(13, 9.6))
        self.fig.canvas.manager.set_window_title("WattsUp NILM Monitor v4 (physical socket)")
        self.fig.patch.set_facecolor("#1e1e1e")

        # 4행 구성: row0=소켓카드, row1=버튼band(카드 바로 아래), row2=오실로스코프, row3=info.
        # 하단 0.0~0.10 은 '모두 OFF'/상태줄 margin.
        gs = self.fig.add_gridspec(
            4, N_PHYS_SOCKETS,
            height_ratios=[1.0, 0.42, 1.3, 0.9],
            hspace=0.45, wspace=0.25,
            left=0.05, right=0.97, top=0.95, bottom=0.10,
        )
        self._gs = gs  # 버튼 band(row1) 셀 위치 계산용 (_build_control_panel)

        # =====================================================
        # 상단: socket 카드 (orchestrator 매핑 사용)
        # =====================================================
        self.socket_axes = []
        self.socket_rects = []
        self.socket_state_labels = []
        self.socket_device_labels = []
        self.socket_power_labels = []

        for i in range(N_PHYS_SOCKETS):
            ax = self.fig.add_subplot(gs[0, i])
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)
            ax.set_xticks([]); ax.set_yticks([])
            ax.set_facecolor("#1e1e1e")
            for spine in ax.spines.values():
                spine.set_edgecolor("gray")
            ax.set_title(f"Socket {i+1}", color="white", fontsize=13,
                         fontweight="bold", pad=8)

            rect = plt.Rectangle(
                (0.05, 0.05), 0.9, 0.9,
                facecolor=self.COLOR_EMPTY,
                edgecolor=self.BORDER_EMPTY,
                linewidth=3,
            )
            ax.add_patch(rect)
            self.socket_rects.append(rect)

            dev_txt = ax.text(0.5, 0.72, "", ha="center", va="center",
                              color="white", fontsize=18, fontweight="bold",
                              transform=ax.transAxes)
            state_txt = ax.text(0.5, 0.5, "EMPTY", ha="center", va="center",
                                color="white", fontsize=20, fontweight="bold",
                                transform=ax.transAxes)
            pwr_txt = ax.text(0.5, 0.22, "", ha="center", va="center",
                              color="#FFFF00", fontsize=16, fontweight="bold",
                              transform=ax.transAxes)
            self.socket_device_labels.append(dev_txt)
            self.socket_state_labels.append(state_txt)
            self.socket_power_labels.append(pwr_txt)
            self.socket_axes.append(ax)

        # =====================================================
        # 중단: oscilloscope (dashboard_ui 와 동일 스타일)
        # =====================================================
        self.ax_scope = self.fig.add_subplot(gs[2, :])
        self.line_ch0, = self.ax_scope.plot(np.zeros(self.buffer_size), color="magenta",
                                             linewidth=1.2, label="Voltage (CH0 - PT)")
        self.line_ch1, = self.ax_scope.plot(np.zeros(self.buffer_size), color="cyan",
                                             linewidth=1.6, label="Current (CH1 - CT)")
        self.ax_scope.set_ylim(-2048, 2048)
        self.ax_scope.set_xlim(0, self.buffer_size)
        self.ax_scope.set_facecolor("black")
        self.ax_scope.set_title("Real-time Oscilloscope", color="white", fontsize=11, pad=6)
        self.ax_scope.legend(loc="upper right", fontsize=10, facecolor="#222")
        self.ax_scope.grid(True, linestyle=":", alpha=0.3, color="gray")
        self.ax_scope.tick_params(colors="white", labelsize=9)
        for spine in self.ax_scope.spines.values():
            spine.set_edgecolor("gray")

        # =====================================================
        # 하단: info text
        # =====================================================
        self.ax_info = self.fig.add_subplot(gs[3, :])
        self.ax_info.set_facecolor("black")
        self.ax_info.set_xticks([]); self.ax_info.set_yticks([])
        for spine in self.ax_info.spines.values():
            spine.set_edgecolor("gray")

        self.info_text = self.ax_info.text(
            0.01, 0.95, "",
            transform=self.ax_info.transAxes,
            color="white", fontsize=10, family="monospace",
            verticalalignment="top",
        )

        # =====================================================
        # 제어 버튼 패널 (mobile_ui 와 동일 기능)
        # =====================================================
        # 한 번에 하나의 동작만 (mobile 의 busy 가드와 동일). 토스트는 background
        # thread 가 문자열만 갱신하고 그리기는 update_frame(메인 스레드)이 담당.
        self._action_busy = False
        self._status_msg = "버튼: 소켓별 ON/OFF · 재스캔 · 모두 OFF  (화면은 자동 새로고침)"
        self._status_kind = "info"          # info / ok / err / warn
        self._status_expire = 0.0           # time.time() 기준 만료 (0 = 유지)
        self.toggle_buttons = []            # 소켓별 ON/OFF 버튼 (라벨/색을 매 frame 갱신)
        self._build_control_panel()

    # =========================================================
    # 제어 버튼 패널 구성
    # =========================================================
    STATUS_COLOR = {
        "info": "#cccccc",
        "ok": "#00E676",
        "err": "#FF5252",
        "warn": "#FFD54F",
    }

    def _build_control_panel(self):
        """소켓 카드 *바로 아래* 에 [ON/OFF | 재추론] 두 버튼을 좌우로 배치.
        하단 margin 에 '모두 OFF' + 상태줄.

        ⚠️ matplotlib 위젯은 참조를 유지하지 않으면 GC 되어 클릭이 동작하지 않는다.
        그래서 모든 Button 을 self 리스트/속성에 보관한다. (이전 버전에서 재추론 버튼이
        로컬 변수라 GC 돼서 '아예 안 눌리던' 버그의 원인.)
        """
        self.rescan_buttons = []
        GAP = 0.012                      # 좌우 버튼 사이 간격 (figure fraction)

        for i in range(N_PHYS_SOCKETS):
            # 카드(row0) 바로 아래 band(row1) 셀의 figure 좌표를 읽어 그 안을 좌우로 2분할.
            pos = self._gs[1, i].get_position(self.fig)
            x0, y0, w, h = pos.x0, pos.y0, pos.width, pos.height
            bw = (w - GAP) / 2.0          # 버튼 폭 (좌/우 균등)
            bh = min(h, 0.05)
            by = y0 + (h - bh) / 2.0      # band 안에서 세로 가운데

            # 왼쪽: ON/OFF 토글 (라벨/색은 update_frame 이 relay 상태로 매 frame 갱신)
            ax_tog = self.fig.add_axes([x0, by, bw, bh])
            btn_tog = Button(ax_tog, "OFF", color="#444444", hovercolor="#666666")
            btn_tog.label.set_color("white")
            btn_tog.label.set_fontsize(11)
            btn_tog.label.set_fontweight("bold")
            btn_tog.on_clicked(lambda _e, sk=i + 1: self._on_toggle(sk))
            self.toggle_buttons.append(btn_tog)

            # 오른쪽: 재추론
            ax_re = self.fig.add_axes([x0 + bw + GAP, by, bw, bh])
            btn_re = Button(ax_re, "재추론", color="#2d3a4a", hovercolor="#3d5570")
            btn_re.label.set_color("#9ec5ff")
            btn_re.label.set_fontsize(10)
            btn_re.on_clicked(lambda _e, sk=i + 1: self._on_rescan(sk))
            self.rescan_buttons.append(btn_re)   # GC 방지 — 반드시 보관

        # 모두 OFF (좌측 하단 margin)
        ax_alloff = self.fig.add_axes([0.05, 0.028, 0.16, 0.045])
        self.btn_alloff = Button(ax_alloff, "모두 OFF", color="#5a2d2d", hovercolor="#7a3d3d")
        self.btn_alloff.label.set_color("white")
        self.btn_alloff.label.set_fontweight("bold")
        self.btn_alloff.on_clicked(lambda _e: self._on_all_off())

        # 상태 토스트 (모두 OFF 우측)
        self.status_text = self.fig.text(
            0.24, 0.050, self._status_msg,
            color=self.STATUS_COLOR["info"], fontsize=10, family="monospace",
            va="center", ha="left",
        )

    # =========================================================
    # 토스트 / busy 동작 디스패치 (mobile 의 busy 가드 + toast 대응)
    # =========================================================
    def _set_status(self, msg, kind="info", ttl=6.0):
        """background thread 가 호출. 문자열만 갱신; 실제 그리기는 update_frame."""
        self._status_msg = msg
        self._status_kind = kind
        self._status_expire = (time.time() + ttl) if ttl else 0.0
        logging.info(f"[DASH BTN] {msg}")

    def _run_action(self, name, fn):
        """동작을 daemon thread 에서 실행 (matplotlib 메인 스레드 블로킹 방지)."""
        if self._action_busy:
            self._set_status("이전 작업 진행 중… 잠시 후 다시 시도하세요", "warn")
            return

        def worker():
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                self._set_status(f"{name} 오류: {e}", "err")
                logging.warning(f"[DASH BTN] {name} 오류: {e}")
            finally:
                self._action_busy = False

        self._action_busy = True
        threading.Thread(target=worker, daemon=True, name="dash_action").start()

    # ---- 버튼 콜백 (mobile_ui 의 toggle / rescan / allOff 와 동일 호출) ----
    def _on_toggle(self, sk):
        relay = self.orchestrator.relay

        def fn():
            new_on = relay.toggle(sk)
            # v65 와 동일: 단순 GPIO 토글이 아니라 orchestrator state 도 동기화.
            try:
                self.orchestrator.on_external_relay_change(sk)
            except Exception as e:  # noqa: BLE001
                logging.warning(f"[DASH BTN] orchestrator sync 실패: {e}")
            self._set_status(f"소켓 {sk} → {'ON' if new_on else 'OFF'}", "ok")

        self._run_action(f"소켓{sk} 토글", fn)

    def _on_rescan(self, sk):
        def fn():
            self._set_status(f"소켓 {sk} 재스캔 중… (릴레이 토글 측정, 몇 초 소요)",
                             "info", ttl=0.0)
            res = self.orchestrator.rescan_socket(sk) or {}
            ok = bool(res.get("ok"))
            msg = res.get("msg") or ("재스캔 완료" if ok else "재스캔 실패")
            self._set_status(f"[S{sk}] {msg}", "ok" if ok else "err")

        self._run_action(f"소켓{sk} 재스캔", fn)

    def _on_all_off(self):
        relay = self.orchestrator.relay

        def fn():
            for sk in range(1, N_PHYS_SOCKETS + 1):
                relay.set(sk, False)
                try:
                    self.orchestrator.on_external_relay_change(sk)
                except Exception as e:  # noqa: BLE001
                    logging.warning(f"[DASH BTN] orchestrator sync 실패(S{sk}): {e}")
            self._set_status("모든 소켓 OFF", "ok")

        self._run_action("모두 OFF", fn)

    # =========================================================
    # Socket card update
    # =========================================================
    def _update_socket_card(self, idx, state, device):
        rect = self.socket_rects[idx]
        dev_lbl = self.socket_device_labels[idx]
        state_lbl = self.socket_state_labels[idx]
        pwr_lbl = self.socket_power_labels[idx]

        face, border = {
            "EMPTY": (self.COLOR_EMPTY, self.BORDER_EMPTY),
            "PENDING": (self.COLOR_PENDING, self.BORDER_PENDING),
            "ASSIGNED": (self.COLOR_ASSIGNED, self.BORDER_ASSIGNED),
            "DEVICE_OFF": (self.COLOR_DEVICE_OFF, self.BORDER_DEVICE_OFF),
        }.get(state, (self.COLOR_EMPTY, self.BORDER_EMPTY))
        rect.set_facecolor(face)
        rect.set_edgecolor(border)

        label_txt, label_color = self.STATE_LABEL.get(state, ("EMPTY", "white"))
        state_lbl.set_text(label_txt)
        state_lbl.set_color(label_color)

        if state in ("ASSIGNED", "DEVICE_OFF") and device:
            dev_lbl.set_text(device.upper())
            if state == "ASSIGNED":
                pwr_lbl.set_text(f"{DEVICE_POWER_W.get(device, 0)} W")
            else:
                pwr_lbl.set_text("0 W")
        elif state == "PENDING":
            dev_lbl.set_text("WAIT")
            pwr_lbl.set_text("")
        else:
            dev_lbl.set_text("")
            pwr_lbl.set_text("")

    # =========================================================
    # Frame update (matplotlib animation callback)
    # =========================================================
    def update_frame(self, _frame):
        # 1) 엔진은 *분류만* 담당 (socket 매핑은 무시).
        # v37: orchestrator 와 SPI race 방지를 위해 engine_lock 으로 보호.
        try:
            with self.orchestrator.engine_lock:
                status = self.engine.process_ai_frame()
        except Exception as e:  # noqa: BLE001
            logging.exception(f"process_ai_frame error: {e}")
            return []

        # 2) UI 의 socket 카드는 orchestrator 의 *물리* 매핑으로 그린다.
        sk_status = self.orchestrator.get_socket_status()
        for i in range(N_PHYS_SOCKETS):
            sk_idx = i + 1
            s = sk_status.get(sk_idx, {"state": "EMPTY", "device": None})
            self._update_socket_card(i, s["state"], s["device"])

        # 3) oscilloscope (engine 의 status 사용)
        ch0 = status.get("ch0") if status else None
        ch1 = status.get("ch1") if status else None
        if ch0 is not None and len(ch0) == self.buffer_size:
            self.line_ch0.set_ydata(ch0)
            self.line_ch1.set_ydata(ch1)

        # 4) info text (engine status + orchestrator last_event)
        if status:
            wf = status.get("win_feat") or {}
            info_lines = [
                "frame: {:>5d}   event: {:<12s}   cooldown: {:>2d}   pending_on: {}   fs: {:>6.1f} Hz".format(
                    status["frame_count"], str(status["event"]),
                    status["event_cooldown"], status.get("pending_on", False),
                    status["fs_actual"]),
                "",
                "baseline  Irms: {:>8.2f}   H1: {:>10.2f}".format(
                    status["baseline_irms"], status["baseline_h1"]),
                "current   Irms: {:>8.2f}   H1: {:>10.2f}   H3: {:>8.2f}   THD: {:.3f}".format(
                    wf.get("Irms_adc_mean", 0), wf.get("H1_60_mag_mean", 0),
                    wf.get("H3_180_mag_mean", 0), wf.get("THD_i_mean", 0)),
                "delta     Irms: {:>+8.2f}   H1: {:>+10.2f}".format(
                    wf.get("Irms_adc_mean", 0) - status["baseline_irms"],
                    wf.get("H1_60_mag_mean", 0) - status["baseline_h1"]),
                "",
                "classifier active : {}".format(status.get("active_devices") or "{}"),
                "physical socket    : {}".format(
                    ", ".join(f"S{i+1}:{sk_status[i+1]['state']}"
                              + (f"({sk_status[i+1]['device']})"
                                 if sk_status[i+1]['device'] else "")
                              for i in range(N_PHYS_SOCKETS))),
                "last orch event    : {}".format(
                    getattr(self.orchestrator, "last_event", "-") or "-"),
            ]
            self.info_text.set_text("\n".join(info_lines))

        # 5) 제어 패널 갱신 — 토글 버튼 라벨/색 (relay 실제 상태 반영) + 상태 토스트.
        #    (mobile UI 가 2초마다 relay state 로 ON/OFF 라벨을 갱신하는 것과 동일.)
        try:
            relay_state = self.orchestrator.relay.get_state()
        except Exception:  # noqa: BLE001
            relay_state = {}
        for i, btn in enumerate(self.toggle_buttons):
            on = bool(relay_state.get(i + 1, False))
            btn.label.set_text("ON" if on else "OFF")
            face = "#00C853" if on else "#444444"
            btn.color = face                 # 다음 hover 복원색
            btn.ax.set_facecolor(face)

        # 상태 토스트 만료 처리
        if self._status_expire and time.time() > self._status_expire:
            self._status_msg = "버튼: 소켓별 ON/OFF · 재스캔 · 모두 OFF  (화면은 자동 새로고침)"
            self._status_kind = "info"
            self._status_expire = 0.0
        busy_prefix = "[작업중] " if self._action_busy else ""
        self.status_text.set_text(busy_prefix + self._status_msg)
        self.status_text.set_color(self.STATUS_COLOR.get(self._status_kind, "#cccccc"))

        out = [self.line_ch0, self.line_ch1]
        out += self.socket_rects + self.socket_state_labels
        out += self.socket_device_labels + self.socket_power_labels
        out += [self.info_text]
        return out

    def start(self):
        self.ani = animation.FuncAnimation(
            self.fig, self.update_frame,
            interval=100,
            blit=False,
            cache_frame_data=False,
        )
        plt.show()
