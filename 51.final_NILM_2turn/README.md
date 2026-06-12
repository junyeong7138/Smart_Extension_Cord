# 51. final_NILM_2turn — TV ramp 이중 등록(swap) 보정

> TV·충전기 같은 저전력(LP) 기기는 켜진 뒤 신호가 **~10초에 걸쳐 서서히 올라가는(ramp)**
> 특성이 있어, 하나의 TV가 **두 번의 ON 이벤트로 쪼개져** 서로 다른 기기 2개로
> 잘못 등록되는 문제를 보정한 버전입니다. ("2turn" = 두 번째 턴의 이벤트 처리)

## What's New (vs 40)

`ai_engine_v2.py` 에 **LP RAMP CONTINUATION swap** 로직 추가:

- 조건: 새로 분류된 기기가 LP(charger/tv)인데, 다른 LP가 이미 active이고
  그 기존 등록이 *신호-only fallback*(불확실 경로)이며, 등록 후 **15초 이내**
- 동작: 새 소켓을 또 할당하지 않고 **기존 등록의 라벨만 교체**(swap),
  signature는 두 이벤트의 delta를 누적해 갱신

```python
LP_RAMP_CONTINUATION_SECONDS = 15.0
LP_RAMP_SWAP_OLD_METHODS = { "low_power_h1_over_rf_*", "low_power_h1_only", ... }
```

orchestrator는 변경 없음 (40과 동일).

## Test Result

드라이기·청소기·TV·충전기 4기기 — ON / OFF / 재-ON(전자레인지 포함) / 재-OFF
시퀀스 정상 동작 확인.

## Run

```bash
python RaspberryPi/main.py
```

## Next

자동 인식이 틀렸을 때 사람이 바로잡을 수단이 필요 → `60.NILM_mobile_reinfer` 재스캔 버튼.
