# 20. WattsUp_NILM — NILM 시작: 수집 → 전처리 → RandomForest

> NILM(Non-Intrusive Load Monitoring) 첫 단계.
> **데이터 수집 → 전처리 → 학습**의 3단계 파이프라인을 만들고
> 단일 기기 분류에서 **정확도 약 90%** 를 확인했습니다.

## Pipeline

```
1.raw_data_collector.py   기기별 RAW 파형 수집 (5초 OFF → 20초 ON 패턴)
        ↓  Data/RAW/*.csv
2.make_summary_from_raw.py 특징 추출/요약 (summary 파일 생성)
        ↓  Data/SUMMARY/*.csv
3.train_device_classifier.py RandomForest 학습 → Model/ 저장
```

## Key Files

| File | Description |
|---|---|
| `RaspberryPi/1.raw_data_collector.py` | 기기별 RAW 데이터 수집 |
| `RaspberryPi/2.make_summary_from_raw.py` | 전처리 — summary 생성 |
| `RaspberryPi/3.train_device_classifier.py` | RandomForest 학습 (n_estimators=300, max_depth=8) |
| `RaspberryPi/main.py` + `spi_core/dsp_engine/dashboard_ui` | 13에서 가져온 실시간 모니터 |
| `Model/rf_device_classifier.joblib` | 학습된 분류기 |
| `Model/rf_device_features.json` | feature 정의 (170개) |

## Targets & Result

- 대상 기기: charger / cooker / dryer / fan
- 단일 기기 분류 정확도 **≈ 90%** — 수집부터 추론까지 전체 흐름 검증 완료

## Next

→ `21.WattsUp_NILM` 에서 기기 *조합* 인식 실험.
