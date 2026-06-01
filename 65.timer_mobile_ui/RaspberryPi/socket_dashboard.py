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
"""

import logging
from functools import partial

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button

# "안정화 중" 팝업 오버레이 (표시 전용 — 분류/cooldown 로직과 무관).
# 파일이 없거나 import 실패해도 대시보드는 그대로 동작하도록 방어.
try:
    from stabilizing_overlay import StabilizingOverlay
except Exception:  # noqa: BLE001
    StabilizingOverlay = None

# 예약 타이머 설정 팝업 (▲▼ 스테퍼). import 실패해도 대시보드는 동작.
try:
    from timer_dialog import TimerDialog
except Exception:  # noqa: BLE001
    TimerDialog = None


def _find_korean_font():
    try:
        from matplotlib import font_manager
        avail = {f.name for f in font_manager.fontManager.ttflist}
        for name in ("NanumGothic", "NanumBarunGothic", "Noto Sans CJK KR",
                     "Malgun Gothic", "AppleGothic", "Apple SD Gothic Neo", "UnDotum"):
            if name in avail:
                return name
    except Exception:  # noqa: BLE001
        pass
    return None


_KO_FONT = _find_korean_font()
if _KO_FONT:
    matplotlib.rcParams["font.family"] = _KO_FONT
matplotlib.rcParams["axes.unicode_minus"] = False
_LBL_RESCAN = "재스캔" if _KO_FONT else "Re-scan"   # matplotlib 폰트엔 이모지 없음 → 텍스트만


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

    # 소켓별 ON/OFF 토글 버튼 색 (relay 실제 상태 반영)
    TOGGLE_ON_FACE = "#1f7a33"
    TOGGLE_OFF_FACE = "#555555"

    STATE_LABEL = {
        "EMPTY": ("EMPTY", "white"),
        "PENDING": ("PENDING", "white"),
        "ASSIGNED": ("ON", "white"),
        "DEVICE_OFF": ("OFF", "white"),
    }

    def __init__(self, engine, orchestrator, timer_manager=None):
        self.engine = engine
        self.orchestrator = orchestrator
        self.timer_manager = timer_manager   # 소켓별 예약 타이머 카운트다운 표시(읽기전용)
        self.buffer_size = getattr(engine, "buffer_size", 150)

        # =====================================================
        # Figure / Grid
        # =====================================================
        self.fig = plt.figure(figsize=(13, 10))
        self.fig.canvas.manager.set_window_title("WattsUp NILM Monitor v4 (physical socket)")
        self.fig.patch.set_facecolor("#1e1e1e")

        # row0: socket 카드 / row1: 소켓별 컨트롤(ON/OFF·재스캔·Timer + 카운트다운)
        # row2: 오실로스코프 / row3: info  (row1 을 키워 2단 버튼 + 카운트다운 공간 확보)
        gs = self.fig.add_gridspec(
            4, N_PHYS_SOCKETS,
            height_ratios=[1.0, 0.85, 1.05, 0.65],
            hspace=0.5, wspace=0.25,
            left=0.05, right=0.97, top=0.95, bottom=0.05,
        )
        self.gs = gs

        # =====================================================
        # 상단: socket 카드 (orchestrator 매핑 사용)
        # =====================================================
        self.socket_axes = []
        self.socket_rects = []
        self.socket_state_labels = []
        self.socket_device_labels = []
        self.socket_power_labels = []
        self.socket_timer_labels = []

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
            # 타이머 카운트다운 라벨은 카드가 아니라 Timer 버튼 밑(_build_socket_controls)에 생성.
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
        # 소켓별 "재스캔" 버튼 (소켓 카드와 오실로스코프 사이)
        # mobile_ui 의 재스캔과 동일 — orchestrator.rescan_socket(sk) 호출.
        # =====================================================
        self._rescan_buttons = []
        self._toggle_buttons = []
        self._timer_buttons = []
        self._ctrl_status = self.fig.text(
            0.5, 0.985, "", ha="center", va="top", color="#9ec5ff", fontsize=10)
        self._build_socket_controls()

        # "안정화 중(Stabilizing)" 팝업 — cooldown>0 동안 0~100% 표시 (맨 위 오버레이).
        self.stab_overlay = StabilizingOverlay(self.fig) if StabilizingOverlay else None
        # 예약 타이머 설정 팝업 (▲▼ 스테퍼). Timer 버튼 클릭 시 show(sk).
        self.timer_dialog = (TimerDialog(self.fig, on_confirm=self._on_timer_confirm)
                             if TimerDialog else None)

    # =========================================================
    # 소켓 컨트롤 (소켓별 ON/OFF 토글 + 재스캔 + Timer + 카운트다운)
    # =========================================================
    def _build_socket_controls(self):
        """row1 밴드에 소켓별 컨트롤 배치 (mobile_ui 와 동일 기능):
            윗줄: [ON/OFF] + [재스캔]   /   아랫줄: [Timer]   /   맨 밑: 카운트다운.
        ON/OFF → relay.toggle + orchestrator 동기, 재스캔 → rescan_socket,
        Timer → timer_dialog.show(sk) → TimerManager 예약."""
        band = self.gs[1, :].get_position(self.fig)
        by0, by1 = band.y0, band.y1
        H = by1 - by0
        # 세로 배치: 윗줄 버튼(ON/OFF·재스캔) → Timer 버튼 → 카운트다운 텍스트
        row_top_y = by0 + H * 0.66      # ON/OFF·재스캔
        row_top_h = H * 0.28
        row_timer_y = by0 + H * 0.34    # Timer
        row_timer_h = H * 0.26
        count_y = by0 + H * 0.13        # 카운트다운 텍스트
        for i in range(N_PHYS_SOCKETS):
            sk = i + 1
            col = self.gs[0, i].get_position(self.fig)
            xL, xR = col.x0, col.x1
            cw = xR - xL
            cx = xL + cw / 2.0
            # 윗줄 왼쪽: ON/OFF 토글 (relay 실제 상태 반영)
            ax_t = self.fig.add_axes([xL + cw * 0.06, row_top_y, cw * 0.42, row_top_h])
            bt = Button(ax_t, "OFF", color=self.TOGGLE_OFF_FACE, hovercolor="#6a6a6a")
            bt.label.set_color("#cccccc")
            bt.label.set_fontsize(11)
            bt.label.set_fontweight("bold")
            bt.on_clicked(partial(self._on_toggle, sk))
            self._toggle_buttons.append(bt)
            # 윗줄 오른쪽: 재스캔
            ax_r = self.fig.add_axes([xL + cw * 0.52, row_top_y, cw * 0.42, row_top_h])
            br = Button(ax_r, _LBL_RESCAN, color="#2d3a4a", hovercolor="#3d5570")
            br.label.set_color("#9ec5ff")
            br.label.set_fontsize(11)
            br.on_clicked(partial(self._on_rescan, sk))
            self._rescan_buttons.append(br)   # 참조 보존 (GC 시 콜백 죽음 방지)
            # 아랫줄: Timer
            ax_tm = self.fig.add_axes([xL + cw * 0.20, row_timer_y, cw * 0.60, row_timer_h])
            btm = Button(ax_tm, "Timer", color="#3a2d4a", hovercolor="#503d66")
            btm.label.set_color("#d6b3ff")
            btm.label.set_fontsize(11)
            btm.label.set_fontweight("bold")
            btm.on_clicked(partial(self._on_timer, sk))
            self._timer_buttons.append(btm)
            # 맨 밑: 카운트다운 텍스트 (Timer 버튼 바로 아래)
            ctxt = self.fig.text(cx, count_y, "", ha="center", va="center",
                                 color="#d6b3ff", fontsize=10, fontweight="bold")
            self.socket_timer_labels.append(ctxt)
        self._refresh_toggle_buttons()

    def _on_timer(self, sk, _event):
        """Timer 버튼: ▲▼ 스테퍼 팝업 열기."""
        if self.timer_dialog is None:
            self._set_status("타이머 다이얼로그 미연결")
            return
        self.timer_dialog.show(sk)

    def _on_timer_confirm(self, sk, action, seconds):
        """타이머 다이얼로그 OK → TimerManager 예약."""
        if self.timer_manager is None:
            self._set_status("타이머 매니저 미연결 (예약 불가)")
            return
        try:
            if seconds <= 0:
                self.timer_manager.cancel_timer(sk)
                self._set_status(f"소켓{sk} 타이머 취소 (00:00:00)")
            else:
                self.timer_manager.set_timer(sk, action, seconds)
                self._set_status(
                    f"소켓{sk} {str(action).upper()} 타이머 {self._fmt_hms(seconds)} 설정")
        except Exception as e:  # noqa: BLE001
            self._set_status(f"소켓{sk} 타이머 오류: {e}")

    def _refresh_toggle_buttons(self):
        """relay 실제 상태로 각 ON/OFF 버튼의 라벨/색 갱신 (외부 토글·자동 OFF 도 반영)."""
        try:
            state = self.orchestrator.relay.get_state()
        except Exception:  # noqa: BLE001
            return
        for i, b in enumerate(self._toggle_buttons):
            on = bool(state.get(i + 1, False))
            b.label.set_text("ON" if on else "OFF")
            face = self.TOGGLE_ON_FACE if on else self.TOGGLE_OFF_FACE
            b.color = face                      # hover 복귀색
            b.ax.set_facecolor(face)            # 현재 표시색
            b.label.set_color("#ffffff" if on else "#cccccc")

    def _on_toggle(self, sk, _event):
        """ON/OFF 버튼: relay 토글 + orchestrator state 동기 (mobile_ui 와 동일)."""
        try:
            self.orchestrator.relay.toggle(sk)
            try:
                self.orchestrator.on_external_relay_change(sk)
            except Exception as e:  # noqa: BLE001
                logging.warning(f"[DASH] orchestrator sync 실패: {e}")
            self._refresh_toggle_buttons()
            on = bool(self.orchestrator.relay.get_state().get(sk, False))
            self._set_status(f"소켓{sk} 릴레이 {'ON' if on else 'OFF'}")
        except Exception as e:  # noqa: BLE001
            self._set_status(f"소켓{sk} 토글 오류: {e}")

    def _on_rescan(self, sk, _event):
        """재스캔 버튼: 해당 소켓만 릴레이 토글 → AI 재분류 (mobile_ui 와 동일 기능)."""
        self._set_status(f"소켓{sk} 재스캔 중...")
        try:
            res = self.orchestrator.rescan_socket(sk)
            msg = (res or {}).get("msg") or f"소켓{sk} 재스캔 완료"
        except Exception as e:  # noqa: BLE001
            msg = f"소켓{sk} 재스캔 오류: {e}"
        self._set_status(msg)

    def _set_status(self, msg):
        try:
            self._ctrl_status.set_text(msg or "")
            self.fig.canvas.draw_idle()
        except Exception:  # noqa: BLE001
            pass
        logging.info(f"[DASH-RESCAN] {msg}")

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

    @staticmethod
    def _fmt_hms(sec):
        sec = max(0, int(sec))
        return f"{sec // 3600:02d}:{(sec % 3600) // 60:02d}:{sec % 60:02d}"

    def _update_timer_labels(self):
        """timer_manager 의 소켓별 남은 시간을 카드 하단에 'OFF in HH:MM:SS' 로 표시."""
        timers = {}
        if self.timer_manager is not None:
            try:
                timers = self.timer_manager.get_timers()
            except Exception:  # noqa: BLE001
                timers = {}
        for i in range(N_PHYS_SOCKETS):
            lbl = self.socket_timer_labels[i]
            t = timers.get(i + 1)
            if t:
                act = "ON" if t.get("action") == "on" else "OFF"
                # matplotlib 폰트엔 이모지 없음 → 텍스트만 (mobile UI 는 ⏱ 사용)
                lbl.set_text(f"TIMER {act} {self._fmt_hms(t.get('remaining', 0))}")
            else:
                lbl.set_text("")

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

        # 2.5) 예약 타이머 카운트다운 (읽기전용 — 설정/취소는 mobile UI 에서)
        self._update_timer_labels()

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

        # ON/OFF 토글 버튼을 relay 실제 상태로 동기 (자동 OFF/재스캔/외부 토글 반영)
        self._refresh_toggle_buttons()

        # "안정화 중" 팝업: cooldown>0 이면 표시(0~100%), 0 이면 숨김. (표시 전용)
        if self.stab_overlay is not None:
            self.stab_overlay.update(status.get("event_cooldown", 0) if status else 0)

        out = [self.line_ch0, self.line_ch1]
        out += self.socket_rects + self.socket_state_labels
        out += self.socket_device_labels + self.socket_power_labels
        out += self.socket_timer_labels
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
