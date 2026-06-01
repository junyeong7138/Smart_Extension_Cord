#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
timer_dialog.py
===============
모니터 UI(socket_dashboard, matplotlib)용 예약 타이머 설정 팝업.

mobile UI 와 동일한 2단계 흐름:
  1) 선택 화면 : [ON timer] [OFF timer] [Cancel]
  2) picker 화면: 시:분:초 (matplotlib 은 휠 picker 가 어려워 ▲/▼ 스테퍼) + [Cancel] [OK]

OK 시 on_confirm(sk, action, seconds) 콜백 → socket_dashboard 가 TimerManager 에 예약.

z-order:
    팝업을 열 때 *배경의 소켓 컨트롤 버튼 axes(bg_axes)* 를 숨긴다. matplotlib 버튼은 hover
    시 자기 axes 를 다시 그리며 위로 올라오는 특성이 있어, 안 숨기면 팝업 뒤 버튼이 팝업 위로
    튀어 올라온다 → bg_axes 를 show 동안 set_visible(False) 로 내려 modal 을 보장.
    팝업 자체 axes 는 backdrop=1000 / 버튼=1002 zorder 로 맨 위.
"""

import matplotlib.patches as mpatches
from matplotlib.widgets import Button


class TimerDialog:
    BACKDROP_RGBA = (0.0, 0.0, 0.0, 0.7)
    CARD_FACE = "#23272e"
    CARD_EDGE = "#8a5cc0"
    NUM_COLOR = "#d6b3ff"
    SEP_COLOR = "#8a5cc0"
    STEP_FACE = "#3a3550"
    ON_FACE = "#2e7d32"
    OFF_FACE = "#b23b3b"

    def __init__(self, fig, on_confirm=None):
        self.fig = fig
        self.on_confirm = on_confirm
        self.bg_axes = []              # 팝업 열 때 숨길 배경 버튼 axes (외부에서 채움)
        self.sk = None
        self.action = "off"
        self.vals = [0, 0, 0]          # [h, m, s]
        self.maxes = [24, 60, 60]
        self.num_x = [0.42, 0.50, 0.58]
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

        # ---- 1단계: 선택 화면 버튼 ----
        self.b_on_choice = self._mkbtn(
            [0.35, 0.555, 0.30, 0.07], "ON timer",
            lambda e: self._choose("on"), face=self.ON_FACE, color="#fff", fs=13)
        self.b_off_choice = self._mkbtn(
            [0.35, 0.455, 0.30, 0.07], "OFF timer",
            lambda e: self._choose("off"), face=self.OFF_FACE, color="#fff", fs=13)
        self.b_cancel_choice = self._mkbtn(
            [0.35, 0.355, 0.30, 0.06], "Cancel",
            lambda e: self.hide(), face="#333333", color="#bbb", fs=12)
        self._choice_axes = [self.b_on_choice.ax, self.b_off_choice.ax,
                             self.b_cancel_choice.ax]

        # ---- 2단계: picker 화면 (시:분:초 + ▲▼ + Cancel/OK) ----
        self._picker_texts = []
        self.num_txt = []
        for x in self.num_x:
            t = self.ax.text(x, 0.50, "00", transform=self.ax.transAxes,
                             ha="center", va="center", color=self.NUM_COLOR,
                             fontsize=26, fontweight="bold", zorder=3)
            self.num_txt.append(t)
            self._picker_texts.append(t)
        for sx in (0.46, 0.54):
            t = self.ax.text(sx, 0.50, ":", transform=self.ax.transAxes,
                             ha="center", va="center", color=self.SEP_COLOR,
                             fontsize=24, fontweight="bold", zorder=3)
            self._picker_texts.append(t)

        self.up_btns, self.dn_btns = [], []
        for i, x in enumerate(self.num_x):
            bu = self._mkbtn([x - 0.035, 0.565, 0.07, 0.045], "▲",
                             (lambda e, idx=i: self._step(idx, +1)),
                             face=self.STEP_FACE, color="#d6b3ff", fs=12)
            bd = self._mkbtn([x - 0.035, 0.40, 0.07, 0.045], "▼",
                             (lambda e, idx=i: self._step(idx, -1)),
                             face=self.STEP_FACE, color="#d6b3ff", fs=12)
            self.up_btns.append(bu)
            self.dn_btns.append(bd)
        self.b_cancel_pick = self._mkbtn(
            [0.31, 0.305, 0.16, 0.055], "Cancel",
            lambda e: self.hide(), face="#333333", color="#bbb", fs=12)
        self.b_ok = self._mkbtn(
            [0.53, 0.305, 0.16, 0.055], "OK",
            lambda e: self._confirm(), face="#8a5cc0", color="#fff", fs=13)
        self._picker_axes = ([b.ax for b in self.up_btns]
                             + [b.ax for b in self.dn_btns]
                             + [self.b_cancel_pick.ax, self.b_ok.ax])

        self._all_btn_axes = self._choice_axes + self._picker_axes

    def _mkbtn(self, rect, label, cb, face="#444", color="#eee", fs=12):
        a = self.fig.add_axes(rect)
        a.set_zorder(1002)
        b = Button(a, label, color=face, hovercolor="#666")
        b.label.set_color(color)
        b.label.set_fontsize(fs)
        b.on_clicked(cb)
        self._btn_refs.append(b)
        return b

    # -----------------------------------------------------------------
    def show(self, sk):
        """선택 화면(1단계)으로 팝업 열기 + 배경 버튼 숨김."""
        self.sk = sk
        self.title.set_text(f"Socket {sk} Timer")
        self._hide_bg(True)
        self.ax.set_visible(True)
        # 1단계: 선택 버튼만
        for a in self._choice_axes:
            a.set_visible(True)
        for a in self._picker_axes:
            a.set_visible(False)
        for t in self._picker_texts:
            t.set_visible(False)
        self._draw()

    def _choose(self, action):
        """ON/OFF timer 선택 → picker 화면(2단계)."""
        self.action = action
        self.vals = [0, 0, 0]
        self.title.set_text(f"Socket {self.sk} · {action.upper()} timer")
        for a in self._choice_axes:
            a.set_visible(False)
        for a in self._picker_axes:
            a.set_visible(True)
        for t in self._picker_texts:
            t.set_visible(True)
        self._refresh_nums()
        self._draw()

    def hide(self, *_):
        self.ax.set_visible(False)
        for a in self._all_btn_axes:
            a.set_visible(False)
        self._hide_bg(False)          # 배경 버튼 복원
        self._draw()

    def is_open(self):
        return self.ax.get_visible()

    def _hide_bg(self, hide):
        for a in self.bg_axes:
            try:
                a.set_visible(not hide)
            except Exception:  # noqa: BLE001
                pass

    def _step(self, idx, delta):
        self.vals[idx] = (self.vals[idx] + delta) % self.maxes[idx]
        self._refresh_nums()
        self._draw()

    def _refresh_nums(self):
        for i, t in enumerate(self.num_txt):
            t.set_text(f"{self.vals[i]:02d}")

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
    print("데모: ON/OFF timer 선택 → ▲▼ 시간 → OK/Cancel. 창 닫으면 종료.")
    plt.show()
