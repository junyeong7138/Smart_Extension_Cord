# 31. old_NILM (cooker + dryer + fan) — 3기기 + State 분류기 실험

> 30을 확장해 밥솥(cooker)까지 3기기를 추적하고,
> **state 분류기(empty / plugged_off / on)** 를 추가한 실험 버전입니다.
> 한계가 드러난 버전이기도 합니다 — 이 실패 분석이 이후 "릴레이 토글 검증" 방식(40~)의 출발점이 됐습니다.

## Architecture (v37)

이중 분류기 구조:
- **State 분류기**: 지금 멀티탭 전체가 empty / plugged_off / on 중 어떤 상태인지 (feature 92개)
- **Device 분류기**: 켜진 기기가 무엇인지 — charger / cooker / dryer / fan (feature 92개)
- delta 추적기가 ON/OFF 이벤트를 슬롯별로 누적 관리

## Key Files

| File | Description |
|---|---|
| `RaspberryPi/ai_extension.py` | v37 — state+device 이중 분류 + delta multi-device tracker |
| `Model/rf_state_classifier.joblib` / `rf_device_classifier.joblib` | state / device 분류기 |
| `RaspberryPi/README.md` | **실측 실행 로그 원본** (2026-05-19, 분석용으로 보존) |

## Result

- ✅ 성공: cooker ON → `cooker_on`, 이어서 dryer ON → `cooker_on + dryer_on`
- ❌ 실패: 그 상태에서 fan 추가 시 감지 못함 (작은 부하가 큰 부하에 묻힘)
- 🐞 버그: 3기기 ON 후 dryer·cooker를 끄면 일시적으로 전부 OFF 표시 → 잠시 후 `fan_on`으로 출렁임

## Lesson Learned

합산 신호의 delta "추측"만으로는 **작은 기기가 큰 기기 위에 얹힌 상황**을 풀 수 없음.
→ 추측 대신 **릴레이를 직접 토글해 물리적으로 확인**하는 방식으로 전환 (`40.final_NILM_1turn`).
분류 대상도 판별이 어려운 cooker/fan을 제외하고 charger/tv/cleaner/microwave/dryer 5종으로 재선정.
