# 67. Watts_viewer — 실시간 전력 + 절약 대기전력 표시

> "이 멀티탭이 지금 얼마나 쓰고, 얼마나 아껴줬는가"를 숫자로 보여주는 버전.
> 대기전력 차단의 효과를 **절약 전력량 누적**으로 시각화합니다.

## What's New (vs 66)

- **실시간 전력 총합(W)** — ON(ASSIGNED) 소켓들의 정격전력 합으로 표시
  (측정 P_proxy는 ADC² 단위라 W 환산 보정이 없어, 사용자 친화적 W는 정격합 사용)
  - 정격 맵: charger 5 / tv 60 / cleaner 600 / microwave 900 / dryer 1800 W
- **절약 대기전력 누적** — DEVICE_OFF(릴레이 차단) 동안 `대기전력 × 시간`을 적산해
  "Standby Saved N W·s (Wh)"로 표시
  - 대기전력 맵: charger 1 / tv 1.5 / microwave 3 / dryer·cleaner 0 W
- **PENDING 30초 자동 만료** — 빈 소켓을 켜두고 안 쓰면 자동 정리 (카운트다운 표시)
- 모니터: 전력 박스(좌 실시간 / 우 절약) + 레이아웃 5행 정리,
  모바일: 전력 카드 2열 동일 구성
- 측정 안정화: 재스캔 OFF 측정에 **동기-펄스**(`_capture_off_pulses`) 도입 —
  짧은 OFF 버스트를 여러 번 반복하며 인접 ON/OFF를 차감해 HP 배경 상쇄

## Key Files

| File | Description |
|---|---|
| `RaspberryPi/socket_orchestrator_v2.py` | 절약 누적/PENDING 만료/동기-펄스 측정 |
| `RaspberryPi/socket_dashboard.py` | 전력 박스 + 5행 레이아웃 |
| `RaspberryPi/mobile_ui.py` | 전력 카드 2열 (실시간 W / 절약 W·s+Wh) |

## Run

```bash
python RaspberryPi/main.py
```

## Next

→ `70.Smart_Extension_Cord` 에서 자체 제작 멀티탭 하드웨어 + 푸시버튼으로 제품 형태 완성.
