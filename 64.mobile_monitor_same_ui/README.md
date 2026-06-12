# 64. mobile_monitor_same_ui — 모바일/모니터 UI 통일

> 폰 화면과 모니터 화면이 **같은 정보, 같은 색, 같은 기능**을 보여주도록 통일한 버전.
> 어느 쪽을 보든 소켓 상태를 동일하게 읽을 수 있습니다.

## What's New (vs 63)

- **소켓 상태 색 통일** (양쪽 동일):
  - PENDING = 파랑 / ON(ASSIGNED) = 초록 / DEVICE_OFF = 주황 / EMPTY = 회색("OFF")
- 모바일에도 모니터와 동일한 기능 세트: **ON/OFF 토글 + 재스캔 + Stabilizing 팝업**
  (모바일 팝업은 HTML/CSS로 동일 의미 구현, cooldown 진행률 표시)
- 모바일 수동 토글이 `on_external_relay_change` 로 orchestrator 상태와 동기화

## Key Files

| File | Description |
|---|---|
| `RaspberryPi/mobile_ui.py` | Flask UI — 디자인/기능 모니터와 통일 |
| `RaspberryPi/socket_dashboard.py` | 모니터 UI — 상태 색/레이아웃 정리 |

## Run

```bash
python RaspberryPi/main.py
# 모니터 + 폰(http://<Pi IP>:5000) 화면이 같은 상태를 보여주는지 확인
```

## Next

→ `65.timer_mobile_ui` / `66.timer_monitor_ui` 에서 예약 타이머 추가.
