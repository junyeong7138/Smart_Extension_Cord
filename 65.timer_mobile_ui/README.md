# 65. timer_mobile_ui — 예약 타이머 (모바일)

> 소켓별 **ON/OFF 예약 타이머**를 추가한 버전 (모바일 UI 우선 구현).
> "30분 뒤 이 소켓 꺼줘" 같은 알람식 예약이 가능해집니다.

## What's New (vs 64)

- **`socket_timer.py`** 신규 — `TimerManager`
  - `set_timer(sk, "on"/"off", seconds)` / `cancel_timer(sk)` / `get_timers()`
  - 백그라운드 스레드가 만기 체크 → `relay.set` + `on_external_relay_change` 자동 발화
    (ON → PENDING, OFF → DEVICE_OFF 전이로 orchestrator와 자연 동기)
- **모바일 타이머 UI**: ⏱ 버튼 → ON/OFF 타이머 선택 → **시:분:초 스크롤 picker** →
  소켓 카드에 실시간 카운트다운 + 취소 버튼
- API: `POST /api/timer/<sk>` (설정) / `POST /api/timer/<sk>/cancel`

## Key Files

| File | Description |
|---|---|
| `RaspberryPi/socket_timer.py` | TimerManager (단독 self-test 내장) |
| `RaspberryPi/timer_dialog.py` | 타이머 설정 팝업 (신규) |
| `RaspberryPi/mobile_ui.py` | 타이머 UI/엔드포인트 (+244줄) |

## Run

```bash
python RaspberryPi/main.py
python RaspberryPi/socket_timer.py   # 타이머 발화/취소 self-test (Mock)
```

## Next

→ `66.timer_monitor_ui` 에서 모니터(matplotlib) 쪽에도 같은 타이머 UI 추가.
