# 66. timer_monitor_ui — 예약 타이머 (모니터)

> 65의 타이머를 **모니터(matplotlib) UI에도** 추가한 버전.
> 마우스 환경에선 스크롤 picker가 불편해서 **▲/▼ 스테퍼 방식**으로 구현했습니다.

## What's New (vs 65)

- `timer_dialog.py` 를 matplotlib용으로 확장:
  - 2단계 흐름 — [ON timer / OFF timer] 선택 → ▲▼ 스테퍼로 시:분:초 설정 → Cancel/OK
  - **off-screen 이동 기법**: 화면 전환 시 안 쓰는 버튼 axes를 화면 밖으로 옮겨
    겹친 버튼이 잘못 눌리는 matplotlib 클릭 디스패치 버그 원천 차단
  - modal 처리: backdrop(zorder 1000) + 팝업 열 때 배경 버튼 숨김
- `socket_dashboard.py`: 소켓별 [Timer] 버튼 + 타이머 카운트다운 라벨 추가

## Key Files

| File | Description |
|---|---|
| `RaspberryPi/timer_dialog.py` | ▲▼ 스테퍼 타이머 팝업 (단독 데모 내장) |
| `RaspberryPi/socket_dashboard.py` | Timer 버튼/카운트다운 (+105줄) |
| `RaspberryPi/socket_timer.py` | 65와 동일 (TimerManager 공유) |

## Run

```bash
python RaspberryPi/main.py
python RaspberryPi/timer_dialog.py   # 팝업 단독 데모
```

## Next

→ `67.Watts_viewer` 에서 실시간 전력/절약 전력량 표시 추가.
