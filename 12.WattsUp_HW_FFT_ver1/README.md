# 12. WattsUp_HW_FFT_ver1 — 하드웨어 FFT 완성 + 실시간 뷰어

> **64-pt Radix-2 FFT를 FPGA에서 완전 구현**한 첫 버전.
> 오실로스코프 모드(1)와 주파수 스펙트럼 모드(2)를 키보드로 전환하며 볼 수 있습니다.

## Overview

- `fft_core_64.v` 완전 재구현: 6-stage Radix-2 나비연산, 비트역순 주소,
  DC 오프셋 제거(0~4095 → −2048~+2047), **더블 버퍼링**(계산용/출력용 RAM 분리)
- 상태머신: `IDLE → LOAD(64샘플) → CALC_FFT(6단계) → CALC_MAG → DONE`
- ADC 샘플링 타이밍 재조정 (`timer_cnt 50000 → 13020`) — 60 Hz 기본파와
  3·5·7차 고조파(180/300/420 Hz)를 Bin 1~16 (30~480 Hz)에서 관측 가능

**실측 결과**: 헤어드라이기는 60 Hz 성분이 뚜렷하고,
노트북 충전기(SMPS)는 3·5·7차 고조파가 도드라짐 — **고조파로 기기를 구별할 수 있다**는
NILM의 핵심 가설이 여기서 확인됐습니다.

## Key Files

| File | Description |
|---|---|
| `FPGA/fft_core_64.v` | 64-pt FFT 코어 (239줄, 완전 구현) |
| `FPGA/fft_butterfly.v` | Q15 복소 곱셈 (32bit 중간값 → 16bit) |
| `FPGA/WattsUp.v`, `adc_ctrl.v`, `SPI_ctrl.v` | 최상위/ADC Master/SPI Slave |
| `RaspberryPi/realtime_viewer.py` | matplotlib 뷰어 — 키 `1`(파형)/`2`(스펙트럼) 전환, Y축 자동 스케일 |

## How to Run

```bash
python3 RaspberryPi/realtime_viewer.py
# 키보드 1: 오실로스코프 모드 / 2: 주파수 스펙트럼 모드
```

## Known Issue & Next

기능은 완성됐지만 파이썬이 한 파일(350줄+)에 몰려 있어 유지보수가 어려움.
→ `13.WattsUp_HW_FFT_ver2` 에서 모듈 분리.
