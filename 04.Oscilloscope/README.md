# 04. Oscilloscope — 전압/전류 실시간 파형 뷰어

> 03에서 만든 FPGA→Pi 데이터 경로에 **실제 센서(ZMPT101B 전압, ACS712 전류)** 를 물리고,
> matplotlib 애니메이션으로 AC 파형을 실시간 확인하는 단계입니다.

## Overview

- 상단 그래프: **전압 파형** (ZMPT101B, 분압비 ≈ 1.606 적용)
- 하단 그래프: **전류 파형** (ACS712 — 오프셋 2.5 V, 감도 0.185 V/A)
- 최근 100 샘플을 deque 로 스크롤 표시, 20 ms 간격 갱신

```
current(mA) = (V_sensor − 2.5) / 0.185 × 1000
voltage(V)  = ADC × 3.3 / 4095 × 1.606
```

## Key Files

| File | Description |
|---|---|
| `FPGA/WattsUp.v`, `adc_ctrl.v`, `SPI_ctrl.v` | 03.ADC_SPI_Check 와 동일 (1 ms 샘플링, 32비트 전송) |
| `RaspberryPi/Oscilloscope.py` | matplotlib FuncAnimation 실시간 뷰어 — SPI 1 MHz 로 상향 |

## How to Run

```bash
# FPGA 비트스트림 로드, 센서 연결 후
python3 RaspberryPi/Oscilloscope.py
# matplotlib 창에 전압/전류 파형이 실시간 표시됨
```

## Result & Next

가전을 꽂으면 60 Hz AC 파형과 부하별 전류 변화가 눈으로 확인됨.
파형의 **고조파 성분**을 분석하려면 FFT가 필요 → `10.FPGA_FFT` 에서 하드웨어 FFT 설계 시작.
