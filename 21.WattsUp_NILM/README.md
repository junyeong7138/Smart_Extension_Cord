# 21. WattsUp_NILM — 단일 기기 인식 완성 + 조합(pair) 모델 실험

> 20의 90% 모델로 **"하나만 꽂혀 있을 때 무엇인지"는 안정적으로 감지**하게 된 버전.
> 동시에 두 기기 조합을 인식하기 위한 pair 분류기를 추가로 실험했습니다.

## What's New (vs 20)

- `ai_extension.py` **신규** — 다중 기기 추적용 AI 엔진의 시작점
- `Model/rf_device_pair_classifier.joblib` **신규** — 기기 2개 조합 분류기
- 단일/조합 모두 feature 170개 (`rf_device_features.json`, `rf_device_pair_features.json`)

## Key Files

| File | Description |
|---|---|
| `RaspberryPi/ai_extension.py` | 실시간 추론 + 다중 기기 상태 추적 엔진 |
| `RaspberryPi/1~3.*.py` | 수집/전처리/학습 파이프라인 (20과 동일 구조) |
| `Model/rf_device_classifier.joblib` | 단일 기기 분류기 |
| `Model/rf_device_pair_classifier.joblib` | 기기 조합(pair) 분류기 |

## Targets & Result

- 대상 기기: charger / cooker / dryer / fan
- 단일 기기 감지: 안정적 ✓
- 조합 모델: 모든 조합을 학습 데이터로 커버하기 어려움 →
  이후 버전(30~)에서 **"합산 신호의 변화량(delta)으로 추적"** 하는 방식으로 전환

## Next

→ `30.old_NILM(dryer+fan)` 에서 delta 기반 다중 기기 추적 검증.
