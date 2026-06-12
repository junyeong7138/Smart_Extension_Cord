# 02. ADC_Check — MCP3202 ADC 단독 검증 (Raspberry Pi)

> FPGA를 거치지 않고 **Raspberry Pi가 직접 MCP3202를 SPI로 제어**해서
> ADC 칩과 측정 회로가 정상인지 먼저 확인하는 단계입니다.

## Overview

MCP3202(12-bit, 2채널)에 3바이트 명령을 보내 채널별 변환값을 읽습니다.

- **CH0**: 전압 측정
- **CH1**: 330 Ω 저항을 거친 전류 측정 (V = I × R 로 환산)

| Channel | Command bytes |
|---|---|
| CH0 | `[0x01, 0xA0, 0x00]` |
| CH1 | `[0x01, 0xE0, 0x00]` |

변환: `V = ADC × 3.3 / 4095`, `I(mA) = V_CH1 / 330 × 1000`

## Key Files

| File | Description |
|---|---|
| `RaspberryPi/ADC_ctrl.py` | MCP3202 직접 제어 — 100 kHz SPI, 0.5초 간격으로 CH0/CH1 RAW 값 + 환산값 출력 |

## How to Run

```bash
# MCP3202 를 Pi SPI 핀에 직접 연결한 상태에서
python3 RaspberryPi/ADC_ctrl.py
```

## Result & Next

두 채널 모두 정상 변환 확인. ADC 제어 시퀀스를 이해했으니
→ `03.ADC_SPI_Check` 에서 **이 제어를 FPGA로 이관**합니다.
