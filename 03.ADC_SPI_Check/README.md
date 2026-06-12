# 03. ADC_SPI_Check — FPGA가 ADC를 제어하고 Pi로 전송

> 01(SPI 통신)과 02(ADC 제어)를 합친 단계.
> **FPGA가 MCP3202를 직접 샘플링**하고, 결과를 SPI로 Raspberry Pi에 보냅니다.
> 이 구조가 최종 제품까지 이어지는 데이터 경로의 원형입니다.

## Overview

```
MCP3202 ──(SPI 500kHz, FPGA가 Master)── FPGA ──(SPI, Pi가 Master)── Raspberry Pi
```

- FPGA 내부 타이머가 **1 ms 주기**로 CH0/CH1을 자동 샘플링
- 32비트 패킷으로 전송: `[0000 + CH0 12bit][0000 + CH1 12bit]`
- Pi는 4바이트를 받아 채널별 12비트를 추출해 전압/전류로 환산

## Key Files

| File | Description |
|---|---|
| `FPGA/WattsUp.v` | 최상위 — 1 ms 샘플링 타이머, 2채널 데이터 32비트 패킹 |
| `FPGA/adc_ctrl.v` | **신규** ADC Master 컨트롤러 — 50 MHz를 분주해 500 kHz SCLK 생성, 17클럭(Start+Cmd+Null+12data) 시퀀스로 MCP3202 읽기 |
| `FPGA/SPI_ctrl.v` | SPI Slave — 전송 폭 8 → **32비트** 확장 |
| `RaspberryPi/ADC_SPI_ctrl.py` | 4바이트 수신 → 채널 분리(`& 0x0FFF`) → 전압/전류 환산 출력 |

## How to Run

```bash
# FPGA 비트스트림 로드 후
python3 RaspberryPi/ADC_SPI_ctrl.py
```

## Result & Next

FPGA 경유 2채널 측정 정상. → `04.Oscilloscope` 에서 이 스트림을 실시간 파형으로 시각화.
