# 13. WattsUp_HW_FFT_ver2 — 파이썬 모듈화 (7주차 캡스톤 제출 버전)

> 기능은 12(ver1)와 동일하고, **파이썬 코드를 역할별 모듈로 분리**한 버전입니다.
> 이 3계층 구조(spi_core / dsp_engine / UI)가 최종 제품까지 그대로 이어집니다.

## Architecture

```
main.py ──► SPICore (spi_core.py)      : SPI 통신 캡슐화
        ──► DSPEngine (dsp_engine.py)  : RAW/FFT 모드 처리, 1920 Hz 샘플 동기화
        ──► DashboardUI (dashboard_ui.py) : matplotlib 실시간 대시보드
```

## Key Files

| File | Description |
|---|---|
| `RaspberryPi/main.py` | 진입점 — 3개 컴포넌트 생성·연결 |
| `RaspberryPi/spi_core.py` | `SPICore` — transfer/close |
| `RaspberryPi/dsp_engine.py` | `DSPEngine` — `process_raw_mode()`(150샘플 프레임), `process_fft_mode()`(Bin 1~16 magnitude) |
| `RaspberryPi/dashboard_ui.py` | `DashboardUI` — 키 입력 모드 전환 + 애니메이션 |
| `FPGA/*` | 12(ver1)와 동일 — 64-pt FFT 하드웨어 |

## Numbers

- 샘플링 ≈ 1920 Hz (샘플 간격 ≈ 520 µs), 프레임 = 150 샘플 (≈ 78 ms)
- FFT 64-pt, 관측 Bin 1~16 (30~480 Hz), 타겟 고조파 60/180/300/420 Hz

## How to Run

```bash
python3 RaspberryPi/main.py
```

## Next

하드웨어 + 신호 파이프라인 완성 → `20.WattsUp_NILM` 부터 **기기 인식(NILM)** 시작.
