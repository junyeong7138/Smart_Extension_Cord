#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
settings_dialog.py
==================
모니터 UI(socket_dashboard, matplotlib)용 Settings 팝업.

2단계 흐름 (timer_dialog 와 동일 패턴):
  1) 메뉴 화면   : [Limit] [About] [Close]
  2-a) Limit 화면: 기기별 안전 자동차단 한도(초) ▲/▼ 스테퍼 + [Cancel] [OK]
       - 0 = 무제한 ("OFF" 표시). step 5s, 상한 MAX_LIMIT_S(30분).
       - OK 시 on_save(limits dict) 콜백 → socket_dashboard 가 safety_limits.json 저장.
  2-b) About 화면: 팀 정보 (Watts Up / Smart NILM Power Strip / Team / since 2026)

modal 처리(off-screen 이동·hovercolor=face·bg_axes 숨김·z-order)는 timer_dialog 와
동일 방식 — 이유/버그 배경은 timer_dialog.py 모듈 docstring 참조.
텍스트는 영어 (Pi 한글폰트 깨짐 방지 원칙).
"""

import os
import sys

import matplotlib.patches as mpatches
from matplotlib.widgets import Button

# safety_limits 는 RaspberryPi/control/ 에 있음 (2026-06-12 폴더 정리) — 단독 실행 대비
_CONTROL_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "control"))
if _CONTROL_DIR not in sys.path:
    sys.path.append(_CONTROL_DIR)
try:
    from safety_limits import DEFAULT_LIMITS_S, MAX_LIMIT_S
    _DEVICES = list(DEFAULT_LIMITS_S.keys())
except Exception:  # noqa: BLE001
    _DEVICES = ["dryer", "microwave", "cleaner", "tv", "charger"]
    MAX_LIMIT_S = 1800

_OFFSCREEN = [2.0, 2.0, 0.01, 0.01]   # figure 좌표 밖 → 클릭/표시 안 됨

TEAM_MEMBERS = ["Junyeong Park", "Haram Kim", "Namhyung Kwon", "Minwoo Lee"]


class SettingsDialog:
    BACKDROP_RGBA = (0.0, 0.0, 0.0, 0.7)
    CARD_FACE = "#23272e"
    CARD_EDGE = "#3d5570"
    VAL_COLOR = "#9ec5ff"
    STEP_FACE = "#2d3a4a"
    STEP_S = 5                  # ▲/▼ 한 번에 5초

    def __init__(self, fig, get_limits=None, on_save=None):
        self.fig = fig
        self.get_limits = get_limits   # () -> {device: seconds} (Limit 화면 열 때 현재값)
        self.on_save = on_save         # (limits dict) -> None    (OK 시 저장 콜백)
        self.bg_axes = []
        self.vals = {d: 0 for d in _DEVICES}
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

        cx0, cy0, cw, ch = 0.26, 0.15, 0.48, 0.68
        self.card = mpatches.FancyBboxPatch(
            (cx0, cy0), cw, ch, transform=self.ax.transAxes,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            facecolor=self.CARD_FACE, edgecolor=self.CARD_EDGE,
            linewidth=2.0, zorder=2)
        self.ax.add_patch(self.card)
        cx = cx0 + cw / 2.0

        self.title = self.ax.text(
            cx, cy0 + ch * 0.93, "Settings", transform=self.ax.transAxes,
            ha="center", va="center", color="white", fontsize=15,
            fontweight="bold", zorder=3)

        # ---- 1단계: 메뉴 화면 ----
        # "Limit" 은 무슨 제한인지 안 읽혀서 기능 목적이 드러나는 이름으로 (2026-06-12)
        self.b_limit = self._mkbtn(
            [0.35, 0.565, 0.30, 0.07], "Overheat Protection",
            lambda e: self._show_limit(), face=self.STEP_FACE,
            color=self.VAL_COLOR, fs=12)
        self.b_about = self._mkbtn(
            [0.35, 0.465, 0.30, 0.07], "About",
            lambda e: self._show_about(), face="#3a3550", color="#d6b3ff", fs=13)
        self.b_close_menu = self._mkbtn(
            [0.35, 0.365, 0.30, 0.06], "Close",
            lambda e: self.hide(), face="#333333", color="#bbb", fs=12)
        self._menu_btns = [self.b_limit, self.b_about, self.b_close_menu]

        # ---- 2-a: Limit 화면 (기기별 ▲/▼ 스테퍼) ----
        self._limit_texts = []
        self.val_txt = {}
        self._limit_up, self._limit_dn = [], []
        row_y = 0.660
        for dev in _DEVICES:
            name_t = self.ax.text(
                0.30, row_y, dev, transform=self.ax.transAxes,
                ha="left", va="center", color="#dddddd", fontsize=12,
                fontweight="bold", zorder=3)
            self._limit_texts.append(name_t)
            bd = self._mkbtn([0.50, row_y - 0.022, 0.055, 0.044], "▼",
                             (lambda e, d=dev: self._step(d, -1)),
                             face=self.STEP_FACE, color=self.VAL_COLOR, fs=11)
            v_t = self.ax.text(
                0.615, row_y, "OFF", transform=self.ax.transAxes,
                ha="center", va="center", color=self.VAL_COLOR, fontsize=14,
                fontweight="bold", zorder=3)
            bu = self._mkbtn([0.68, row_y - 0.022, 0.055, 0.044], "▲",
                             (lambda e, d=dev: self._step(d, +1)),
                             face=self.STEP_FACE, color=self.VAL_COLOR, fs=11)
            self.val_txt[dev] = v_t
            self._limit_texts.append(v_t)
            self._limit_dn.append(bd)
            self._limit_up.append(bu)
            row_y -= 0.066
        hint_t = self.ax.text(
            cx, 0.345, "auto-off after N seconds · 0 = no limit",
            transform=self.ax.transAxes, ha="center", va="center",
            color="#888888", fontsize=9, zorder=3)
        self._limit_texts.append(hint_t)
        self.b_cancel_limit = self._mkbtn(
            [0.33, 0.255, 0.16, 0.055], "Cancel",
            lambda e: self.show(), face="#333333", color="#bbb", fs=12)
        self.b_ok_limit = self._mkbtn(
            [0.51, 0.255, 0.16, 0.055], "OK",
            lambda e: self._confirm(), face="#2e7d32", color="#fff", fs=13)
        self._limit_btns = (self._limit_up + self._limit_dn
                            + [self.b_cancel_limit, self.b_ok_limit])

        # ---- 2-b: About 화면 (팀 정보) ----
        self._about_texts = [
            self.ax.text(cx, 0.660, "Watts Up", transform=self.ax.transAxes,
                         ha="center", va="center", color="white", fontsize=22,
                         fontweight="bold", zorder=3),
            self.ax.text(cx, 0.595, "Smart NILM Power Strip",
                         transform=self.ax.transAxes, ha="center", va="center",
                         color="#7CFC7C", fontsize=12, zorder=3),
            self.ax.text(cx, 0.520, "T e a m", transform=self.ax.transAxes,
                         ha="center", va="center", color="#888888", fontsize=10,
                         zorder=3),
        ]
        name_y = 0.475
        for name in TEAM_MEMBERS:
            self._about_texts.append(
                self.ax.text(cx, name_y, name, transform=self.ax.transAxes,
                             ha="center", va="center", color="#dddddd",
                             fontsize=13, zorder=3))
            name_y -= 0.040
        self._about_texts.append(
            self.ax.text(cx, 0.295, "since 2026", transform=self.ax.transAxes,
                         ha="center", va="center", color="#888888", fontsize=11,
                         style="italic", zorder=3))
        self.b_back_about = self._mkbtn(
            [0.42, 0.215, 0.16, 0.055], "Back",
            lambda e: self.show(), face="#333333", color="#bbb", fs=12)
        self._about_btns = [self.b_back_about]

        self._all_btns = self._menu_btns + self._limit_btns + self._about_btns

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

    def _set_texts(self, texts, show):
        for t in texts:
            t.set_visible(show)

    def _screen(self, menu=False, limit=False, about=False):
        self._place(self._menu_btns, menu)
        self._place(self._limit_btns, limit)
        self._place(self._about_btns, about)
        self._set_texts(self._limit_texts, limit)
        self._set_texts(self._about_texts, about)

    # -----------------------------------------------------------------
    def show(self, *_):
        """메뉴 화면(1단계)으로 팝업 열기 + 배경 버튼 숨김. (Limit/About 의 Back 도 여기로)"""
        self.title.set_text("Settings")
        self._hide_bg(True)
        self.ax.set_visible(True)
        self._screen(menu=True)
        self._draw()

    def _show_limit(self):
        """Limit 화면: 현재 한도값을 get_limits() 로 받아 표시 (편집은 OK 까지 로컬)."""
        cur = {}
        if self.get_limits is not None:
            try:
                cur = dict(self.get_limits() or {})
            except Exception:  # noqa: BLE001
                cur = {}
        for dev in _DEVICES:
            try:
                self.vals[dev] = max(0, min(MAX_LIMIT_S, int(cur.get(dev, 0))))
            except (TypeError, ValueError):
                self.vals[dev] = 0
        self.title.set_text("Overheat Protection (auto-off, seconds)")
        self._screen(limit=True)
        self._refresh_vals()
        self._draw()

    def _show_about(self):
        self.title.set_text("About")
        self._screen(about=True)
        self._draw()

    def hide(self, *_):
        self.ax.set_visible(False)
        self._screen()                # 전부 off-screen
        self._hide_bg(False)
        self._draw()

    def is_open(self):
        return self.ax.get_visible()

    def _hide_bg(self, hide):
        """배경 버튼 axes 를 숨기기/복원 — set_visible 에 더해 *off-screen 이동* 필수.

        matplotlib Button 은 press 시 ax.contains(event) 로 mouse grab 을 잡는데,
        contains 는 visibility 를 검사하지 않아 set_visible(False) 만으로는 숨겨진
        배경 버튼(먼저 등록됨)이 클릭을 선점, 팝업 버튼 대신 배경 버튼이 발화한다
        (실측 2026-06-12: Settings>Limit 클릭이 뒤 Timer 버튼을 눌러 타이머 팝업이
        열림). 홈 위치 저장 후 off-screen 이동으로 contains 자체를 차단한다.
        timer_dialog._hide_bg 와 동일 구현 (양쪽이 bg_axes 리스트 공유).
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

    # -----------------------------------------------------------------
    def _step(self, dev, direction):
        v = int(self.vals.get(dev, 0)) + direction * self.STEP_S
        self.vals[dev] = min(MAX_LIMIT_S, max(0, v))
        self._refresh_vals()
        self._draw()

    def _refresh_vals(self):
        for dev, t in self.val_txt.items():
            v = int(self.vals.get(dev, 0))
            t.set_text("OFF" if v <= 0 else f"{v}s")

    def _confirm(self):
        """OK: 편집된 한도를 on_save 콜백으로 전달 (dashboard 가 파일 저장) 후 닫기."""
        limits = dict(self.vals)
        self.hide()
        if self.on_save is not None:
            try:
                self.on_save(limits)
            except Exception:  # noqa: BLE001
                pass

    def _draw(self):
        try:
            self.fig.canvas.draw_idle()
        except Exception:  # noqa: BLE001
            pass


# =====================================================================
# 단독 데모 (Mac: MPLBACKEND=Agg 면 렌더 검증만, GUI 백엔드면 인터랙티브)
# =====================================================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(11, 8))
    fig.patch.set_facecolor("#1e1e1e")
    ax = fig.add_subplot(111)
    ax.set_facecolor("black")
    ax.set_title("dummy monitor (settings dialog demo)", color="white")

    def fake_get():
        return {"dryer": 30, "microwave": 60, "cleaner": 90, "tv": 0, "charger": 0}

    def fake_save(limits):
        print(f"[DEMO] save limits: {limits}")

    dlg = SettingsDialog(fig, get_limits=fake_get, on_save=fake_save)
    dlg.show()
    plt.show()
