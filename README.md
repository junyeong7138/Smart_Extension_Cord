# ⚡ WattsUp — Smart Extension Cord with NILM

![Project Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![Hardware](https://img.shields.io/badge/Hardware-FPGA_%7C_Raspberry_Pi-blue)
![Language](https://img.shields.io/badge/Language-Verilog_%7C_Python-green)
![ML](https://img.shields.io/badge/ML-RandomForest_(NILM)-purple)

## 📌 Project Overview

**WattsUp** is a smart multi-tap extension cord that monitors, analyzes, and manages
household power in real time — built with an FPGA for high-speed signal acquisition
and a Raspberry Pi for AI-based appliance recognition.

전류/전압 파형 하나만 보고 **어떤 가전이 어느 소켓에 꽂혀 있는지**를
NILM(Non-Intrusive Load Monitoring)으로 스스로 알아내고,
**대기전력 차단 · 과열 방지 · 예약 타이머 · 음성 알림**까지 수행하는
전자공학 캡스톤 디자인 프로젝트입니다.

> Team **Watts Up** — Junyeong Park · Haram Kim · Namhyung Kwon · Minwoo Lee · since 2026

## 🎯 Key Features

- **Real-Time AC Monitoring** — ZMPT101B(전압) + ACS712(전류) 센서, MCP3202 12-bit ADC
- **Hardware FFT** — FPGA에서 1920 Hz 샘플링 + 64-pt Radix-2 FFT를 직접 연산, SPI로 전송
- **NILM Appliance Recognition** — 고조파(H1/H3/H5/H7)·전력 특징 28개 기반 RandomForest 분류
  (charger / tv / cleaner / microwave / dryer)
- **Socket Identification** — 릴레이를 짧게 토글(동기-펄스, OFF ≈ 33 ms)해 물리 소켓 위치를 확정
- **Standby Power Cut-off** — 기기가 꺼지면 소켓 릴레이 자동 차단, 절약 전력량 누적 표시
- **Overheat Protection** — 기기별 연속 동작 한도(드라이기 등) 초과 시 자동 차단, 80%부터 경고
- **Timers & Sound Alerts** — 소켓별 ON/OFF 예약, 꺼짐 임박 시 음성 + 삐빅 알람 (모니터/모바일)
- **Self-Healing Recognition** — 오인식 의심 시 자동 재검증(auto-verify) + 수동 재스캔 버튼
- **Dual UI** — matplotlib 모니터 대시보드 + Flask 모바일 웹 (실시간 오실로스코프 포함)

## 🏗️ System Architecture

```
1. Sensing Layer      AC 220V → ZMPT101B(V) · ACS712(I) → MCP3202 ADC
2. Hardware Layer     FPGA DE2-115 (Verilog) — 1920 Hz 샘플링, 64-pt FFT, SPI Slave
                        · SPI 프로토콜: 0x01 = RAW 파형 / 0x02 = FFT 결과
3. Application Layer  Raspberry Pi 4 (Python) — SPI Master
                        · AIEngine: RandomForest 기기 분류
                        · SocketOrchestrator: 릴레이 토글 소켓 식별 / 자동 OFF / 과열 방지
                        · UI: 모니터(matplotlib) + 모바일(Flask :5000) + 4ch Relay + 버튼 2개
```

## 📂 Repository Structure

폴더 번호 = 개발 단계입니다. 순서대로 읽으면 모듈 검증부터 제품 완성까지의
과정이 이어집니다. 각 폴더의 `README.md`에 상세 설명이 있습니다.

| Phase | Folder | Summary |
|---|---|---|
| **0. HW Bring-up** | `01.SPI_Check` | FPGA ↔ Pi SPI 통신 첫 검증 (버튼 → Pi) |
| | `02.ADC_Check` | Pi 단독으로 MCP3202 ADC 읽기 |
| | `03.ADC_SPI_Check` | FPGA가 ADC 제어 → Pi로 2채널 전송 |
| | `04.Oscilloscope` | 전압/전류 실시간 오실로스코프 (matplotlib) |
| **1. HW FFT** | `10.FPGA_FFT` | 64-pt FFT 하드웨어 설계 시작 (스켈레톤) |
| | `11.FFT_Mode_Change` | RAW(0x01) ↔ FFT(0x02) 모드 전환 검증 |
| | `12.WattsUp_HW_FFT_ver1` | **FFT 완전 구현** + 파형/스펙트럼 뷰어 |
| | `13.WattsUp_HW_FFT_ver2` | 파이썬 모듈화 (spi_core/dsp_engine/UI 분리) |
| **2. NILM 학습** | `20.WattsUp_NILM` | 수집→전처리→RandomForest 파이프라인 (정확도 90%) |
| | `21.WattsUp_NILM` | 기기 조합(pair) 모델 실험 |
| | `30.old_NILM(dryer+fan)` | 2기기 동시 추적 검증 |
| | `31.old_NILM(cooker+dryer+fan)` | 3기기 + state 분류기 실험 |
| | `99.Collect_NILM` | 학습 데이터 수집 전용 스냅샷 |
| **3. 멀티탭 통합** | `40.final_NILM_1turn` | 릴레이 토글 소켓 식별 + 자동 OFF 1차 완성 |
| | `51.final_NILM_2turn` | TV ramp 이중 등록(swap) 보정 |
| | `60.NILM_mobile_reinfer` | 모바일 **재스캔** 버튼 (수동 재추론) |
| | `61.relay_toggle_time` | 릴레이 OFF 체류를 시간 기반으로 |
| | `62.relay_toggle_sub_frame` | **서브프레임(33 ms) 측정** — TV 재부팅 방지 |
| **4. UX** | `63.stabilizing_ui` | "Stabilizing…" 안정화 팝업 |
| | `64.mobile_monitor_same_ui` | 모바일/모니터 UI 디자인·기능 통일 |
| | `65.timer_mobile_ui` | 예약 타이머 (모바일) |
| | `66.timer_monitor_ui` | 예약 타이머 (모니터, ▲▼ 스테퍼) |
| | `67.Watts_viewer` | 실시간 전력 + 절약 대기전력 표시 |
| **5. 제품 완성** | `70.Smart_Extension_Cord` | 자체 제작 4구 멀티탭 + 푸시버튼 2개 통합 |
| | `71.Smart_Extension_Cord_v2` | 반응속도 개선 (cooldown 단축) |
| | `72.Smart_Extension_Cord_v3` | 토글 잔류 릴레이 정리 — **시연 골든 버전** |
| | `73.Smart_Extension_Cord_v4` | **과열 방지** + Settings + 폴더 구조 정리 |
| | `74.Smart_Extension_Cord_v4.1` | **소리 알림** (음성 + 삐빅, 모니터/모바일) |
| | `75.Smart_Extension_Cord_v5` | **자가 정정(auto-verify)** + 안정화 — ⭐ 최종 |
| Docs | `00.Docs` | 부품 데이터시트 (DE2-115, MCP3202, 센서 등) |

## 🚀 Roadmap & Milestones

- [x] Phase 1: SPI communication between FPGA and Raspberry Pi
- [x] Phase 2: ADC interfacing & sensor calibration (ZMPT101B / ACS712)
- [x] Phase 3: Real-time waveform visualization (oscilloscope)
- [x] Phase 4: Hardware 64-pt FFT & harmonic feature extraction
- [x] Phase 5: NILM — RandomForest appliance classification (5 devices)
- [x] Phase 6: Smart relay control — socket identification & standby cut-off
- [x] Phase 7: UX — timers, power/savings viewer, unified mobile/monitor UI
- [x] Phase 8: Productization — overheat protection, sound alerts, self-healing recognition

## 🔧 Hardware

| Part | Role |
|---|---|
| Terasic **DE2-115** (Cyclone IV EP4CE115) | ADC 제어 · 1920 Hz 샘플링 · 64-pt FFT · SPI Slave |
| **Raspberry Pi 4 Model B** | NILM 추론 · 릴레이/버튼 제어 · 모니터/모바일 UI |
| **MCP3202** | 12-bit 2ch ADC (CH0 전압 / CH1 전류) |
| **ZMPT101B** / **ACS712** | AC 전압 / 전류 센서 |
| 4ch Relay + Push Button ×2 | 소켓 전원 제어 / 일괄 활성화 · 전체 차단 |

## ▶️ Quick Start (최종 버전 = `75.Smart_Extension_Cord_v5`)

```bash
# Raspberry Pi (FPGA 비트스트림 로드 후)
cd 75.Smart_Extension_Cord_v5/RaspberryPi
python main.py        # 모니터 UI 실행 + 모바일 UI(http://<Pi IP>:5000) 자동 기동
```

---
*Developed by Team Watts Up (Electronics Engineering Capstone Design, 2026)*
