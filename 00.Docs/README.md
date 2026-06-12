# 00. Docs — Datasheets

프로젝트에서 사용하는 부품들의 데이터시트 모음입니다.

## Contents (`Datasheet/`)

| File | Part | Used for |
|---|---|---|
| `DE2_115_User_manual.pdf` | Terasic DE2-115 (Cyclone IV) | FPGA 개발보드 — 핀맵/클럭 참조 |
| `RaspberryPi4_datasheet.pdf` | Raspberry Pi 4 Model B | GPIO/SPI 핀 참조 |
| `MCP3202_datasheet.pdf` | MCP3202 | 12-bit 2ch ADC — SPI 프로토콜/타이밍 |
| `ZMPT101B_datasheet.pdf` | ZMPT101B | AC 전압 센서 (CH0) |
| `ACS712_datasheet.pdf` | ACS712 | 홀센서 방식 전류 센서 (CH1) — 감도 0.185 V/A |

## Notes

- ADC 명령어 시퀀스, SPI 모드(Mode 0), 센서 오프셋(ACS712 0 A = 2.5 V) 같은
  코드 상수들은 전부 이 데이터시트에 근거합니다.
- 회로/센서 관련 수치가 의심될 때 가장 먼저 볼 곳.
