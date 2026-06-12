# 70. Smart_Extension_Cord — 자체 제작 멀티탭 + 푸시버튼 통합 (v1)

> 소프트웨어를 **자체 제작 4구 멀티탭 하드웨어**에 올리고,
> 터치센서를 **물리 푸시버튼 2개**로 교체해 제품 형태를 완성한 첫 버전입니다.

## What's New (vs 67)

- **푸시버튼 2개** (GPIO5 / GPIO6, 터치센서 대체):
  - **버튼1**: EMPTY/DEVICE_OFF 소켓을 일괄 PENDING(릴레이 ON) — "기기 꽂을 준비"
  - **버튼2**: 무조건 전체 OFF — 모든 릴레이 차단 + 상태 리셋 (`on_all_off`)
- LP 식별 보강 (`ai_engine_v2`): **LP 부호 override** — idle 전류 오프셋 드리프트로
  dI 부호만 뒤집힌 진짜 TV ON을 dH1 크기로 구제
- 67의 기능 전부 포함: 전력 박스, 절약 누적, 타이머, 재스캔(동기-펄스), Stabilizing 팝업

## Hardware

자체 제작 4구 멀티탭 — 소켓별 릴레이 4ch + 전압/전류 센서 + 푸시버튼 2개 + FPGA/Pi.

## Test Result

- ✅ charger + tv + dryer: ON/OFF/소켓 위치 모두 정확
- ⚠️ 4기기 동시 ON에서 charger(5W) 제거 시 자동 감지 실패
  — 대형 부하 노이즈 바닥 아래라 물리적으로 어려운 영역 (수동 재스캔으로 정정 가능)

## Run

```bash
python RaspberryPi/main.py
```

## Next

→ `71(v2)`: 반응속도 개선 → `72(v3)`: 시연 골든 → `73(v4)+`: 과열 방지/소리/자가정정.
