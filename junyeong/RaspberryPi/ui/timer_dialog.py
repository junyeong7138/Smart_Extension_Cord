#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
timer_dialog.py
===============
모니터 UI(socket_dashboard, matplotlib)용 예약 타이머 설정 팝업.

mobile UI 와 동일한 2단계 흐름:
  1) 선택 화면 : [ON timer] [OFF timer] [Cancel]
  2) picker 화면: 시:분:초 (▲/▼ 스테퍼) + [Cancel] [OK]

OK 시 on_confirm(sk, action, seconds) 콜백 → socket_dashboard 가 TimerManager 에 예약.

중요 — 화면 전환 시 *안 쓰는 화면의 버튼 axes 를 화면 밖으로 이동*시킨다(set_position).
matplotlib 의 클릭 디스패치는 겹친 axes 중 하나만 inaxes 로 고르는데, picker 의 ▲ 가
선택화면 'ON timer' 버튼과 같은 위치에 겹쳐 있으면 ▲ 대신 'ON timer' 가 눌리는 버그가
생긴다(▲ 눌렀는데 팝업이 선택화면으로 돌아감). off-screen 이동으로 겹침을 원천 제거.

성능 — 모든 버튼 hovercolor=face 로 두어 마우스 hover 시 전체 figure redraw(렉)를 막는다.

z-order: 팝업 열 때 배경 소켓 컨트롤 버튼(bg_axes)을 숨겨 modal 보장(hover 시 뒤 버튼이
팝업 위로 튀어오르는 것 방지). 팝업 axes 는 backdrop=1000 / 버튼=1002.
"""

import matplotlib.patches as mpatches
from matplotlib.widgets import Button

_OFFSCREEN = [2.0, 2.0, 0.01, 0.01]   # figure 좌표 밖 → 클릭/표시 안 됨


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
        self.bg_axes = []
        self.sk = None
        self.action = "off"
        self.vals = [0, 0, 0]
        self.maxes = [24, 60, 60]
        self.num_x = [0.42, 0.50, 0.58]
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

        # ---- 1단계: 선택 화면 ----
        self.b_on_choice = self._mkbtn(
            [0.35, 0.555, 0.30, 0.07], "ON timer",
            lambda e: self._choose("on"), face=self.ON_FACE, color="#fff", fs=13)
        self.b_off_choice = self._mkbtn(
            [0.35, 0.455, 0.30, 0.07], "OFF timer",
            lambda e: self._choose("off"), face=self.OFF_FACE, color="#fff", fs=13)
        self.b_cancel_choice = self._mkbtn(
            [0.35, 0.355, 0.30, 0.06], "Cancel",
            lambda e: self.hide(), face="#333333", color="#bbb", fs=12)
        self._choice_btns = [self.b_on_choice, self.b_off_choice, self.b_cancel_choice]

        # ---- 2단계: picker 화면 ----
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
        self._picker_btns = (self.up_btns + self.dn_btns
                             + [self.b_cancel_pick, self.b_ok])

        self._all_btns = self._choice_btns + self._picker_btns

    def _mkbtn(self, rect, label, cb, face="#444", color="#eee", fs=12):
        a = self.fig.add_axes(rect)
        a.set_zorder(1002)
        # hovercolor=face → hover 시 색 안 바뀜 → 전체 redraw(렉) 안 일어남
        b = Button(a, label, color=face, hovercolor=face)
        b.label.set_color(color)
        b.label.set_fontsize(fs)
        b.on_clicked(cb)
        b._home_rect = list(rect)     # 화면 복귀용 home 위치
        return b

    # -----------------------------------------------------------------
    def _place(self, btns, show):
        """버튼 그룹을 화면 안(home)/밖(offscreen)으로. off 면 클릭·표시 둘 다 차단."""
        for b in btns:
            if show:
                b.ax.set_position(b._home_rect)
                b.ax.set_visible(True)
            else:
                b.ax.set_position(_OFFSCREEN)
                b.ax.set_visible(False)

    def show(self, sk):
        """선택 화면(1단계)으로 팝업 열기 + 배경 버튼 숨김."""
        self.sk = sk
        self.title.set_text(f"Socket {sk} Timer")
        self._hide_bg(True)
        self.ax.set_visible(True)
        self._place(self._choice_btns, True)
        self._place(self._picker_btns, False)
        for t in self._picker_texts:
            t.set_visible(False)
        self._draw()

    def _choose(self, action):
        """ON/OFF timer 선택 → picker 화면(2단계)."""
        self.action = action
        self.vals = [0, 0, 0]
        self.title.set_text(f"Socket {self.sk} · {action.upper()} timer")
        self._place(self._choice_btns, False)
        self._place(self._picker_btns, True)
        for t in self._picker_texts:
            t.set_visible(True)
        self._refresh_nums()
        self._draw()

    def hide(self, *_):
        self.ax.set_visible(False)
        self._place(self._choice_btns, False)
        self._place(self._picker_btns, False)
        self._hide_bg(False)
        self._draw()

    def is_open(self):
        return self.ax.get_visible()

    def _hide_bg(self, hide):
        """배경 버튼 axes 를 숨기기/복원 — set_visible 에 더해 *off-screen 이동* 필수.

        matplotlib Button 은 press 시 ax.contains(event) 로 mouse grab 을 잡는데,
        contains 는 visibility 를 검사하지 않는다. 그래서 set_visible(False) 만으로는
        숨겨진 배경 버튼이 클릭을 선점(grab)해 팝업 버튼이 안 눌리고 release 때 배경
        버튼이 발화하는 버그가 생긴다 (실측 2026-06-12: Settings>Limit 클릭이 뒤에
        숨은 Timer 버튼을 눌러 타이머 팝업이 열림). 홈 위치를 저장해 두고 off-screen
        으로 옮겨 contains 자체를 차단한다 (팝업 자체 버튼들의 _place 와 동일 기법).
        """
        for a in self.bg_axes:
            try:
                if hide:
                    if getattr(a, "_dlg_home_pos", None) is None:
                        a._dlg_home_pos = a.get_position().frozen()
                    a.set_position(_OFFSCREEN)
                    a.set_visible(False)
                else:
                    home = getattr(a, "_dlg_home_pos", None)
                    if home is not None:
                        a.set_position(home)
                    a.set_visible(True)
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
    plt.show()
