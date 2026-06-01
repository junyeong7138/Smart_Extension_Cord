#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stabilizing_overlay.py
======================
모니터 UI(socket_dashboard, matplotlib) 위에 띄우는 "안정화 중(Stabilizing)" 팝업 오버레이.

배경
----
AIEngine 의 `event_cooldown` 은 토글 식별 / OFF 검증 / 가짜 트리거 방지 등으로 잠시 올라가는
프레임 카운터다. cooldown 이 0 보다 크면 그동안은 새 ON/OFF event 를 일부러 무시(억제)하므로
"정상적인 기기 판별"이 일시적으로 보류된 상태다. cooldown 이 0 으로 떨어져야 정상 판별이 된다.

일반 사용자는 이 내부 숫자를 모르므로, cooldown > 0 인 동안 화면 중앙에 반투명 팝업을 띄워
  - "Stabilizing..." 문구
  - 0% → 100% 진행률 (cooldown 이 줄어들수록 100% 에 가까워짐)
를 보여주고, cooldown 이 0 이 되면(=100%) 팝업을 자동으로 숨긴다.

로직(분류/cooldown 계산)은 전혀 건드리지 않는다 — *표시 전용* 오버레이.

사용법 (socket_dashboard 등 matplotlib UI 에서)
-----------------------------------------------
    from stabilizing_overlay import StabilizingOverlay
    self.stab_overlay = StabilizingOverlay(self.fig)   # __init__ 에서 1회
    ...
    # 매 프레임 update 콜백에서:
    self.stab_overlay.update(status.get("event_cooldown", 0))

`update(cooldown)` 한 줄만 매 프레임 호출하면 표시/숨김/퍼센트가 알아서 갱신된다.
"""

import matplotlib.patches as mpatches


class StabilizingOverlay:
    """matplotlib figure 위에 그리는 '안정화 중' 팝업 (cooldown 0~100% 진행률).

    cooldown 한 episode(0→N→…→0) 동안 처음 본 최댓값을 peak 로 잡고
    percent = (1 - cooldown/peak) * 100 으로 진행률을 만든다. cooldown 이 다시
    더 큰 값으로 튀면 peak 도 갱신(=다시 안정화 시작)된다. cooldown 0 이면 숨김.
    """

    # 색상 (어두운 대시보드 테마와 맞춤)
    BACKDROP_RGBA = (0.0, 0.0, 0.0, 0.55)   # 화면 전체를 살짝 어둡게
    CARD_FACE = "#23272e"
    CARD_EDGE = "#4caf50"
    BAR_BG = "#3a3f47"
    BAR_FG = "#4caf50"
    TEXT_MAIN = "#ffffff"
    TEXT_PCT = "#4caf50"
    TEXT_SUB = "#aab2bd"

    # 카드 위치/크기 (figure 좌표 0~1)
    CARD_X, CARD_Y, CARD_W, CARD_H = 0.28, 0.37, 0.44, 0.26
    # 진행률 바 (figure 좌표; 카드 중앙, 퍼센트와 보조문구 사이)
    BAR_X, BAR_Y, BAR_W, BAR_H = 0.35, 0.445, 0.30, 0.028

    def __init__(self, fig, title="Stabilizing...", subtitle="please wait"):
        self.fig = fig
        self._peak = 0          # 현재 episode 의 cooldown 최댓값
        self._visible = False

        # 전체 figure 를 덮는 오버레이 axes (제일 위 zorder)
        self.ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=1000)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis("off")
        self.ax.set_facecolor("none")
        self.ax.patch.set_alpha(0.0)

        # 1) 화면 전체 반투명 backdrop
        self.backdrop = mpatches.Rectangle(
            (0, 0), 1, 1, transform=self.ax.transAxes,
            facecolor=self.BACKDROP_RGBA, edgecolor="none", zorder=1,
        )
        self.ax.add_patch(self.backdrop)

        # 2) 중앙 카드
        self.card = mpatches.FancyBboxPatch(
            (self.CARD_X, self.CARD_Y), self.CARD_W, self.CARD_H,
            transform=self.ax.transAxes,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            facecolor=self.CARD_FACE, edgecolor=self.CARD_EDGE, linewidth=2.0,
            zorder=2,
        )
        self.ax.add_patch(self.card)

        cx = self.CARD_X + self.CARD_W / 2.0

        # 3) "Stabilizing..." 메인 문구 (맨 위)
        self.title_text = self.ax.text(
            cx, self.CARD_Y + self.CARD_H * 0.80, title,
            transform=self.ax.transAxes, ha="center", va="center",
            color=self.TEXT_MAIN, fontsize=19, fontweight="bold", zorder=3,
        )

        # 4) 퍼센트 (제목과 바 사이)
        self.pct_text = self.ax.text(
            cx, self.CARD_Y + self.CARD_H * 0.55, "0%",
            transform=self.ax.transAxes, ha="center", va="center",
            color=self.TEXT_PCT, fontsize=22, fontweight="bold", zorder=4,
        )

        # 5) 진행률 바 (배경 + 채움)
        self.bar_bg = mpatches.Rectangle(
            (self.BAR_X, self.BAR_Y), self.BAR_W, self.BAR_H,
            transform=self.ax.transAxes, facecolor=self.BAR_BG,
            edgecolor="none", zorder=3,
        )
        self.bar_fg = mpatches.Rectangle(
            (self.BAR_X, self.BAR_Y), 0.0, self.BAR_H,
            transform=self.ax.transAxes, facecolor=self.BAR_FG,
            edgecolor="none", zorder=4,
        )
        self.ax.add_patch(self.bar_bg)
        self.ax.add_patch(self.bar_fg)

        # 6) 보조 문구 (맨 아래)
        self.sub_text = self.ax.text(
            cx, self.CARD_Y + self.CARD_H * 0.16, subtitle,
            transform=self.ax.transAxes, ha="center", va="center",
            color=self.TEXT_SUB, fontsize=10, zorder=3,
        )

        self._set_visible(False)

    # -----------------------------------------------------------------
    def _set_visible(self, vis):
        self._visible = bool(vis)
        self.ax.set_visible(self._visible)

    def _set_percent(self, percent):
        percent = max(0.0, min(100.0, float(percent)))
        self.pct_text.set_text(f"{percent:.0f}%")
        self.bar_fg.set_width(self.BAR_W * (percent / 100.0))

    # -----------------------------------------------------------------
    def update(self, cooldown):
        """매 프레임 호출. cooldown(int) 에 따라 팝업 표시/퍼센트/숨김을 갱신.

        반환: 그려진(또는 토글된) artist 리스트 — blit 사용 시 활용 가능(미사용도 무방).
        """
        try:
            cd = int(cooldown)
        except (TypeError, ValueError):
            cd = 0

        if cd <= 0:
            # 안정화 완료 → 100% 의미, 팝업 숨김 + episode 리셋
            if self._visible:
                self._set_percent(100.0)
                self._set_visible(False)
            self._peak = 0
            return self._artists()

        # cooldown > 0: 안정화 중
        if cd > self._peak:
            self._peak = cd       # 새 episode 시작 / 더 큰 값으로 재안정화
        peak = max(self._peak, 1)
        percent = (1.0 - cd / peak) * 100.0
        self._set_percent(percent)
        if not self._visible:
            self._set_visible(True)
        return self._artists()

    def _artists(self):
        return [self.ax, self.backdrop, self.card,
                self.title_text, self.pct_text,
                self.bar_bg, self.bar_fg, self.sub_text]


# =====================================================================
# 단독 실행 데모 (가짜 cooldown 30→0 으로 팝업 동작 확인)
# =====================================================================
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib import animation

    fig = plt.figure(figsize=(10, 7))
    fig.patch.set_facecolor("#1e1e1e")
    ax = fig.add_subplot(111)
    ax.set_facecolor("black")
    ax.plot([0, 1, 2, 3], [0, 1, 0, 1], color="cyan")
    ax.set_title("dummy monitor (overlay demo)", color="white")

    overlay = StabilizingOverlay(fig)

    # 가짜 cooldown: 0 에서 시작, 5프레임마다 30 으로 튀고 1씩 감소 반복
    state = {"cd": 0, "tick": 0}

    def fake(_f):
        state["tick"] += 1
        if state["cd"] <= 0 and state["tick"] % 40 == 0:
            state["cd"] = 30          # 새 안정화 episode 시작
        elif state["cd"] > 0:
            state["cd"] -= 1
        overlay.update(state["cd"])
        return []

    _ani = animation.FuncAnimation(fig, fake, interval=100, blit=False,
                                   cache_frame_data=False)
    print("데모: 주기적으로 cooldown 30→0 으로 감소하며 팝업이 떴다 사라짐. 창을 닫으면 종료.")
    plt.show()
