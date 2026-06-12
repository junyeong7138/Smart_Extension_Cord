# 30. old_NILM (dryer + fan) — 다중 기기 추적 첫 검증

> 다중 기기 NILM의 시작.
> 조합 모델 대신 **ON/OFF 이벤트의 변화량(delta)을 추적**하는 방식으로 전환해
> 드라이기 + 선풍기 2기기 동시 인식에 성공한 버전입니다.

## Approach

- 학습은 **단일 기기 데이터만** 사용 (RAW: 5초 OFF → 20초 ON 수집, 합성 다중기기 데이터 미사용)
- 실시간에서는 합산 신호의 **변화량**으로 "방금 뭔가 켜졌다/꺼졌다"를 감지하고
  그 delta를 분류기에 넣어 어떤 기기인지 판별 → 기기별 ON/OFF 상태를 누적 추적

## Key Files

| File | Description |
|---|---|
| `RaspberryPi/ai_extension.py` | delta 기반 다중 기기 추적 엔진 (단순화 버전) |
| `RaspberryPi/main.py`, `dsp_engine.py`, `spi_core.py`, `dashboard_ui.py` | 실시간 모니터 |
| `Model/rf_device_classifier.joblib` | 단일 기기 분류기 (feature 20개) |
| `RaspberryPi/1~3.*.py` | 수집/전처리/학습 코드 (백업 동봉) |

## Result

- **dryer + fan 조합: 완벽 인식** ✓
- 다른 기기 조합은 아직 불안정 — 기기 추가 실험은 31에서 계속

## Next

→ `31.old_NILM(cooker+dryer+fan)` 에서 3기기 + state 분류기 실험.
