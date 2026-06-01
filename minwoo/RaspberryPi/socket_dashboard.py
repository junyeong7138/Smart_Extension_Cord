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
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import power_meter


# Device → 표시용 전력 (UI 에만 사용)
# 실시간 추정이 불가능할 때(보정/win_feat 없음) 정격 fallback 으로만 사용.
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
        self.fig = plt.figure(figsize=(13, 9))
        self.fig.canvas.manager.set_window_title("WattsUp NILM Monitor v4 (physical socket)")
        self.fig.patch.set_facecolor("#1e1e1e")

        gs = self.fig.add_gridspec(
            3, N_PHYS_SOCKETS,
            height_ratios=[1.0, 1.3, 0.9],
            hspace=0.45, wspace=0.25,
            left=0.05, right=0.97, top=0.94, bottom=0.05,
        )

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
        self.ax_scope = self.fig.add_subplot(gs[1, :])
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
        self.ax_info = self.fig.add_subplot(gs[2, :])
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

    # =========================================================
    # Socket card update
    # =========================================================
    def _update_socket_card(self, idx, state, device, power_w=None):
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
                # 실시간 추정 W (power_meter). 추정 불가 시 정격 fallback.
                if power_w is not None:
                    pwr_lbl.set_text(f"{power_w:.0f} W")
                else:
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
        #    각 기기의 실시간 추정 전력(W)은 power_meter 가 계산 (engine 상태 불변).
        sk_status = self.orchestrator.get_socket_status()
        try:
            dev_power = power_meter.per_device_power_w(self.engine)
        except Exception as e:  # noqa: BLE001
            logging.debug(f"per_device_power_w 실패: {e}")
            dev_power = {}
        for i in range(N_PHYS_SOCKETS):
            sk_idx = i + 1
            s = sk_status.get(sk_idx, {"state": "EMPTY", "device": None})
            pw = dev_power.get(s["device"]) if s.get("device") else None
            self._update_socket_card(i, s["state"], s["device"], power_w=pw)

        # 3) oscilloscope (engine 의 status 사용)
        ch0 = status.get("ch0") if status else None
        ch1 = status.get("ch1") if status else None
        if ch0 is not None and len(ch0) == self.buffer_size:
            self.line_ch0.set_ydata(ch0)
            self.line_ch1.set_ydata(ch1)

        # 4) info text (engine status + orchestrator last_event)
        if status:
            wf = status.get("win_feat") or {}
            try:
                total_w = power_meter.total_power_w(self.engine)
            except Exception:  # noqa: BLE001
                total_w = 0.0
            info_lines = [
                "frame: {:>5d}   event: {:<12s}   cooldown: {:>2d}   pending_on: {}   fs: {:>6.1f} Hz".format(
                    status["frame_count"], str(status["event"]),
                    status["event_cooldown"], status.get("pending_on", False),
                    status["fs_actual"]),
                "",
                "total real power  : {:>8.0f} W   (멀티탭 전체 실시간 추정)".format(total_w),
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
