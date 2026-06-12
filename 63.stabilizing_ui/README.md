# 63. stabilizing_ui — "Stabilizing…" 안정화 팝업

> 릴레이 토글이나 이벤트 직후에는 엔진이 `event_cooldown` 동안 판별을 보류하는데,
> 사용자 입장에선 "왜 반응이 없지?"로 보입니다.
> 이 대기 상태를 **0~100% 진행률 팝업**으로 보여줘 기다리게 만든 버전입니다.

## What's New (vs 62)

- **`stabilizing_overlay.py`** 신규 — matplotlib 모니터 UI 위에 띄우는
  "Stabilizing…" 반투명 팝업 (표시 전용, 분류/cooldown 로직은 무변경)
  - `event_cooldown > 0` 이면 표시, 0이 되면 자동으로 사라짐
  - cooldown 최대값을 peak로 잡아 진행률(%)을 적응형 계산
- `socket_dashboard.py` 가 overlay를 optional import (없어도 동작)

## Key Files

| File | Description |
|---|---|
| `RaspberryPi/stabilizing_overlay.py` | 안정화 팝업 (단독 데모: `python stabilizing_overlay.py`) |
| `RaspberryPi/socket_dashboard.py` | 팝업 통합 |

## Run

```bash
python RaspberryPi/main.py
# 릴레이 토글/이벤트 직후 "Stabilizing... N%" 팝업 확인
```

## Next

→ `64.mobile_monitor_same_ui` 에서 이 팝업을 포함해 모바일/모니터 UI를 통일.
