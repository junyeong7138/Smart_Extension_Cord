#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
timer_dialog.py
===============
모니터 UI(socket_dashboard, matplotlib)용 예약 타이머 설정 팝업.

mobile UI 는 스크롤 시:분:초 picker 지만, matplotlib 는 휠 picker 가 어려우므로
▲/▼ 스테퍼 버튼으로 시:분:초를 올리고 내린다. ON/OFF 선택 + 취소/OK.

OK 시 on_confirm(sk, action, seconds) 콜백 호출 → socket_dashboard 가 TimerManager 에
예약을 건다. (분류/orchestrator 로직과 무관한 표시·입력 전용.)

zorder 설계:
    backdrop overlay axes = 1000  (전 화면 덮어 modal — 바깥 클릭은 무효)
    dialog 버튼 axes       = 1002  (backdrop 위 → 클릭 가능)
숨김 시 모든 dialog axes set_visible(False) → 밑의 소켓 컨트롤 버튼이 다시 동작.
"""

import matplotlib.patches as mpatches
from matplotlib.widgets import Button


class TimerDialog:
    BACKDROP_RGBA = (0.0, 0.0, 0.0, 0.6)
    CARD_FACE = "#23272e"
    CARD_EDGE = "#8a5cc0"
    NUM_COLOR = "#d6b3ff"
    SEP_COLOR = "#8a5cc0"
    STEP_FACE = "#3a3550"
    ON_FACE = "#2e7d32"
    OFF_FACE = "#b23b3b"
    DIM_FACE = "#444444"

    def __init__(self, fig, on_confirm=None):
        self.fig = fig
        self.on_confirm = on_confirm
        self.sk = None
        self.action = "off"
        self.vals = [0, 0, 0]          # [h, m, s]
        self.maxes = [24, 60, 60]
        self.num_x = [0.42, 0.50, 0.58]  # 세 컬럼 x (figure/axes 좌표 동일: ax=[0,0,1,1])
        self._btn_refs = []
        self._build()
        self.hide()

    # -----------------------------------------------------------------
    def _build(self):
        self.ax = self.fig.add_axes([0, 0, 1, 1], zorder=1000)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis("off")
        self.ax.patch.set_alpha(0.0)

        self.backdrop = mpatches.Rectangle(
            (0, 0), 1, 1, transform=self.ax.transAxes,
            facecolor=self.BACKDROP_RGBA, edgecolor="none", zorder=1)
        self.ax.add_patch(self.backdrop)

        cx0, cy0, cw, ch = 0.26, 0.27, 0.48, 0.47
        self.card = mpatches.FancyBboxPatch(
            (cx0, cy0), cw, ch, transform=self.ax.transAxes,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            facecolor=self.CARD_FACE, edgecolor=self.CARD_EDGE,
            linewidth=2.0, zorder=2)
        self.ax.add_patch(self.card)
        cx = cx0 + cw / 2.0

        self.title = self.ax.text(
            cx, cy0 + ch * 0.88, "Timer", transform=self.ax.transAxes,
            ha="center", va="center", color="white", fontsize=15,
            fontweight="bold", zorder=3)

        # 시:분:초 숫자 + 구분자 ":"
        self.num_txt = []
        for x in self.num_x:
            t = self.ax.text(x, 0.50, "00", transform=self.ax.transAxes,
                             ha="center", va="center", color=self.NUM_COLOR,
                             fontsize=26, fontweight="bold", zorder=3)
            self.num_txt.append(t)
        for sx in (0.46, 0.54):
            self.ax.text(sx, 0.50, ":", transform=self.ax.transAxes,
                         ha="center", va="center", color=self.SEP_COLOR,
                         fontsize=24, fontweight="bold", zorder=3)

        # ON / OFF 선택 버튼
        self.b_on = self._mkbtn([0.375, 0.625, 0.11, 0.05], "ON",
                                lambda e: self._set_action("on"),
                                face=self.ON_FACE, color="#fff", fs=12)
        self.b_off = self._mkbtn([0.515, 0.625, 0.11, 0.05], "OFF",
                                 lambda e: self._set_action("off"),
                                 face=self.OFF_FACE, color="#fff", fs=12)

        # ▲ / ▼ 스테퍼 (컬럼별)
        self.up_btns, self.dn_btns = [], []
        for i, x in enumerate(self.num_x):
            bu = self._mkbtn([x - 0.035, 0.555, 0.07, 0.045], "▲",
                             (lambda e, idx=i: self._step(idx, +1)),
                             face=self.STEP_FACE, color="#d6b3ff", fs=12)
            bd = self._mkbtn([x - 0.035, 0.395, 0.07, 0.045], "▼",
                             (lambda e, idx=i: self._step(idx, -1)),
                             face=self.STEP_FACE, color="#d6b3ff", fs=12)
            self.up_btns.append(bu)
            self.dn_btns.append(bd)

        # 취소 / OK
        self.b_cancel = self._mkbtn([0.31, 0.305, 0.16, 0.055], "Cancel",
                                    lambda e: self.hide(),
                                    face="#333333", color="#bbb", fs=12)
        self.b_ok = self._mkbtn([0.53, 0.305, 0.16, 0.055], "OK",
                                lambda e: self._confirm(),
                                face="#8a5cc0", color="#fff", fs=13)

        self._dialog_axes = (
            [self.ax]
            + [b.ax for b in (self.b_on, self.b_off, self.b_cancel, self.b_ok)]
            + [b.ax for b in self.up_btns]
            + [b.ax for b in self.dn_btns]
        )

    def _mkbtn(self, rect, label, cb, face="#444", color="#eee", fs=12):
        a = self.fig.add_axes(rect)
        a.set_zorder(1002)
        b = Button(a, label, color=face, hovercolor="#666")
        b.label.set_color(color)
        b.label.set_fontsize(fs)
        b.on_clicked(cb)
        self._btn_refs.append(b)   # GC 방지
        return b

    # -----------------------------------------------------------------
    def show(self, sk):
        self.sk = sk
        self.vals = [0, 0, 0]
        self.action = "off"
        try:
            self.title.set_text(f"Socket {sk} Timer")
        except Exception:  # noqa: BLE001
            pass
        self._refresh()
        for ax in self._dialog_axes:
            ax.set_visible(True)
        self._draw()

    def hide(self, *_):
        for ax in getattr(self, "_dialog_axes", []):
            ax.set_visible(False)
        self._draw()

    def is_open(self):
        return self.ax.get_visible()

    def _set_action(self, action):
        self.action = action
        self._refresh()

    def _step(self, idx, delta):
        self.vals[idx] = (self.vals[idx] + delta) % self.maxes[idx]
        self._refresh()

    def _refresh(self):
        for i, t in enumerate(self.num_txt):
            t.set_text(f"{self.vals[i]:02d}")
        on_sel = (self.action == "on")
        self.b_on.color = self.ON_FACE if on_sel else self.DIM_FACE
        self.b_on.ax.set_facecolor(self.b_on.color)
        self.b_off.color = self.OFF_FACE if not on_sel else self.DIM_FACE
        self.b_off.ax.set_facecolor(self.b_off.color)
        self._draw()

    def _confirm(self):
        sk, action = self.sk, self.action
        seconds = self.vals[0] * 3600 + self.vals[1] * 60 + self.vals[2]
        self.hide()
        if self.on_confirm is not None:
            try:
                self.on_confirm(sk, action, seconds)
            except Exception:  # noqa: BLE001
                pass

    def _draw(self):
        try:
            self.fig.canvas.draw_idle()
        except Exception:  # noqa: BLE001
            pass


# =====================================================================
# 단독 데모
# =====================================================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(11, 8))
    fig.patch.set_facecolor("#1e1e1e")
    ax = fig.add_subplot(111)
    ax.set_facecolor("black")
    ax.set_title("dummy monitor (timer dialog demo)", color="white")

    def confirmed(sk, action, seconds):
        print(f"[DEMO] socket{sk} {action} in {seconds}s")

    dlg = TimerDialog(fig, on_confirm=confirmed)
    dlg.show(3)
    print("데모: ON/OFF + ▲▼ 로 시간 조정, OK/Cancel. 창 닫으면 종료.")
    plt.show()
