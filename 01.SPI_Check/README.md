# 01. SPI_Check — FPGA ↔ Raspberry Pi SPI 통신 검증

> Phase 0 첫 단계. FPGA의 버튼 입력을 SPI로 Raspberry Pi에 전송해
> **두 보드 간 통신 경로가 정상인지** 확인합니다.

## Overview

FPGA(DE2-115)의 푸시버튼 4개(KEY0~3)를 모니터링하다가, 버튼이 눌리면
해당 버튼의 식별 바이트를 SPI Slave로 Raspberry Pi(Master)에 전송합니다.
Pi는 값이 바뀔 때만 버튼 번호를 콘솔에 출력합니다.

| Button | TX Byte |
|---|---|
| KEY0 | `0xA1` |
| KEY1 | `0xB2` |
| KEY2 | `0xC3` |
| KEY3 | `0xD4` |

## Key Files

| File | Description |
|---|---|
| `FPGA/WattsUp.v` | 최상위 모듈 — 버튼 디바운싱 + 엣지 감지 + LED 토글 (50 MHz) |
| `FPGA/SPI_ctrl.v` | SPI Slave (Mode 0) — CS 하강 시 데이터 장전, SCLK 에지마다 1비트 출력. 3단 FF 동기화로 메타스테빌리티 방지 |
| `RaspberryPi/SPI_ctrl.py` | SPI Master — 500 kHz로 1바이트 폴링, 값 변화 시 버튼 인덱스 출력 |

## How to Run

```bash
# 1. FPGA 에 비트스트림 합성/다운로드 (Quartus)
# 2. Raspberry Pi 에서 SPI 활성화 (raspi-config)
python3 RaspberryPi/SPI_ctrl.py
# FPGA 버튼을 누르면 "Button 0 pressed!" 식으로 출력
```

## Hardware

- FPGA: DE2-115 (Cyclone IV), 50 MHz
- Raspberry Pi 4 Model B — SPI bus 0, device 0, Mode 0, 500 kHz

## Result & Next

버튼 → SPI → 콘솔 출력 정상 확인. → `02.ADC_Check` 에서 ADC(MCP3202) 제어로 진행.
