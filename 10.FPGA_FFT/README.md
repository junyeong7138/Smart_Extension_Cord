# 10. FPGA_FFT — 하드웨어 64-pt FFT 설계 시작

> 전류 파형의 고조파(60/180/300/420 Hz)를 분석하기 위해
> **FPGA 안에서 64-point FFT를 직접 연산**하는 설계를 시작한 단계입니다.
> (이 폴더는 골격 설계 — 실제 나비연산 완성은 `12.WattsUp_HW_FFT_ver1`)

## Overview

- SPI 명령 프로토콜 도입: **`0x01` = RAW 모드 / `0x02` = FFT 모드**
- 64-pt Radix-2 FFT 코어 + 나비연산기 + Twiddle Factor ROM 구조 설계
- 이 시점의 FFT 코어는 상태머신 골격만 있고 테스트 패턴(`BEEFCAFE`)을 반환

## Key Files

| File | Description |
|---|---|
| `FPGA/WattsUp.v` | 최상위 — ADC/FFT/SPI 통합, 모드 명령 해석 |
| `FPGA/fft_core_64.v` | 64-pt FFT 코어 (상태머신 골격) |
| `FPGA/fft_butterfly.v` | 나비연산기 — Q15 고정소수점 복소 곱셈 |
| `FPGA/twiddle_re.mem` / `twiddle_im.mem` | Twiddle Factor ROM (Q15) |
| `FPGA/adc_ctrl.v`, `SPI_ctrl.v` | 04와 동일 계열 (ADC Master / SPI Slave) |
| `RaspberryPi/make_twiddle.py` | Twiddle Factor `.mem` 생성 스크립트 (Q15: −32768~32767) |

## Numbers

- FFT: 64-point, Q15 고정소수점
- SPI: Mode 0, 2 MHz
- 샘플링 타이머: `timer_cnt == 50000` (초기값 — 12번에서 재조정)

## Next

→ `11.FFT_Mode_Change` 에서 RAW/FFT 모드 전환부터 검증.
