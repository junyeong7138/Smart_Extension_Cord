# 11. FFT_Mode_Change — RAW ↔ FFT 모드 전환 검증

> 10에서 설계한 SPI 명령 프로토콜이 실제로 동작하는지 확인하는 단계.
> **`1` 입력 → RAW 데이터 / `2` 입력 → FFT(임시) 데이터**가 정상 전환되는지 테스트합니다.

## Overview

Raspberry Pi에서 모드 바이트를 보내고 FPGA의 응답 형식을 확인합니다.

| Mode | Command | FPGA Response |
|---|---|---|
| RAW | `0x01` | CH0(상위 12bit) + CH1(하위 12bit) 실측값 |
| FFT | `0x02` | 임시 테스트 패턴 (FFT 코어 미완 — 12에서 실데이터로 교체) |

## Key Files

| File | Description |
|---|---|
| `FPGA/*` | 10.FPGA_FFT 와 동일 구조 (FFT 코어는 아직 스켈레톤) |
| `RaspberryPi/test_mode.py` | 키보드로 모드 선택 → 5회 수집 → 16진수로 응답 출력 |

## How to Run

```bash
python3 RaspberryPi/test_mode.py
# [1] RAW / [2] FFT 선택 → 응답 바이트 확인
```

## Result & Next

모드 전환 프로토콜 정상 동작 확인.
→ `12.WattsUp_HW_FFT_ver1` 에서 진짜 FFT 연산 구현 + 실시간 시각화.
