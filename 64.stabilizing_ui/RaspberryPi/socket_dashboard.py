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
        self.fig = plt.figure(figsize=(13, 10))
        self.fig.canvas.manager.set_window_title("WattsUp NILM Monitor v4 (physical socket)")
        self.fig.patch.set_facecolor("#1e1e1e")

        # row0: socket 카드 / row1: 소켓별 재스캔 버튼 / row2: 오실로스코프 / row3: info
        gs = self.fig.add_gridspec(
            4, N_PHYS_SOCKETS,
            height_ratios=[1.0, 0.45, 1.25, 0.85],
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
        # 소켓별 "재스캔" 버튼 (소켓 카드와 오실로스코프 사이)
        # mobile_ui 의 재스캔과 동일 — orchestrator.rescan_socket(sk) 호출.
        # =====================================================
        self._rescan_buttons = []
        self._ctrl_status = self.fig.text(
            0.5, 0.985, "", ha="center", va="top", color="#9ec5ff", fontsize=10)
        self._build_rescan_controls()

        # "안정화 중(Stabilizing)" 팝업 — cooldown>0 동안 0~100% 표시 (맨 위 오버레이).
        self.stab_overlay = StabilizingOverlay(self.fig) if StabilizingOverlay else None

    # =========================================================
    # 재스캔 컨트롤 (소켓별)
    # =========================================================
    def _build_rescan_controls(self):
        """row1 밴드에 소켓별 [🔄 재스캔] 버튼 생성. → orchestrator.rescan_socket(sk)."""
        band = self.gs[1, :].get_position(self.fig)
        by0, by1 = band.y0, band.y1
        h = (by1 - by0) * 0.62
        y = by0 + (by1 - by0) * 0.20
        for i in range(N_PHYS_SOCKETS):
            sk = i + 1
            col = self.gs[0, i].get_position(self.fig)
            xL, xR = col.x0, col.x1
            cw = xR - xL
            ax = self.fig.add_axes([xL + cw * 0.12, y, cw * 0.76, h])
            b = Button(ax, _LBL_RESCAN, color="#2d3a4a", hovercolor="#3d5570")
            b.label.set_color("#9ec5ff")
            b.label.set_fontsize(11)
            b.on_clicked(partial(self._on_rescan, sk))
            self._rescan_buttons.append(b)   # 참조 보존 (GC 시 콜백 죽음 방지)

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

        # "안정화 중" 팝업: cooldown>0 이면 표시(0~100%), 0 이면 숨김. (표시 전용)
        if self.stab_overlay is not None:
            self.stab_overlay.update(status.get("event_cooldown", 0) if status else 0)

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
