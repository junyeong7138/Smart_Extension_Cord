# 62. relay_toggle_sub_frame — 서브프레임 측정 (TV 재부팅 해결)

> 61의 하한(1프레임 = 78 ms)을 깨기 위해 **dsp_engine에 서브프레임 리더를 추가**,
> 릴레이 OFF 체류를 **64샘플 ≈ 33 ms**까지 줄여 TV 재부팅을 막은 버전입니다.

## What's New (vs 61)

- `dsp_engine.py` 에 **`read_raw_subframe(n_samples)`** 신규 —
  150샘플 풀프레임 대신 원하는 샘플 수만 읽기 (동일한 520 µs 게이팅/디코드/fs 보정)
- 재스캔 OFF 측정이 단일 서브프레임으로:

```python
RESCAN_OFF_SAMPLES  = 64      # OFF 측정 샘플 수. 64 ≈ 33ms (32의 배수 권장 — 60Hz bin 정렬)
RESCAN_OFF_SETTLE_S = 0.005   # OFF 후 측정 전 안정화 (짧게)
```

- 서브프레임의 FFT 고조파 크기는 window 길이에 비례하므로 150 등가로 스케일 보정

## Result

- ✅ **TV가 재부팅되지 않음** — OFF 체류 33 ms는 TV PSU hold-up 안쪽
- ⚠️ 남은 문제: 청소기가 꽂혀만 있고 드라이기가 켜진 상태에서 TV를 재스캔하면
  충전기로 오인식 — 대형 부하(HP) 배경 위에서 소형(LP) 신호가 찌그러지는 물리 한계.
  → 이후 70번대에서 **동기-펄스 측정**(인접 ON/OFF 차감으로 배경 상쇄)으로 해결

## Run

```bash
python RaspberryPi/main.py
```
