# ⚡ Smart Extension Cord: Power Analysis & Management System (WattsUp)

![Project Status](https://img.shields.io/badge/Status-In_Development-orange)
![Hardware](https://img.shields.io/badge/Hardware-FPGA_%7C_Raspberry_Pi-blue)
![Language](https://img.shields.io/badge/Language-Verilog_%7C_Python-green)

## 📌 Project Overview
**WattsUp** is a smart multi-tap extension cord system designed to monitor, analyze, and manage household power consumption in real-time. By integrating an FPGA for high-speed hardware control and a Raspberry Pi for data processing, this system aims to recognize appliance usage patterns, calculate power consumption accurately, and provide intelligent power management features.

This project is developed as an Electronics Engineering Capstone Design project.

## 🎯 Final Goals & Key Features
- **Real-Time AC Monitoring:** Measure high-voltage AC current and voltage seamlessly using ZMPT101B (PT) and ACS712 (CT) sensors.
- **High-Speed Data Acquisition:** Utilize an FPGA to handle precise ADC sampling and fast SPI communication.
- **Power Analytics:** Calculate active power, reactive power, and power factor to analyze the true energy consumption of connected appliances.
- **Appliance Profiling (Future):** Analyze waveform signatures to identify which appliance is currently plugged in and running.
- **Smart Control (Future):** Implement standby power cut-off and over-current protection for energy efficiency and electrical safety.
- **Live Visualization:** Provide a real-time web-based oscilloscope and data dashboard for users.

## 🏗️ System Architecture
1. **Sensing Layer:** AC 220V -> ZMPT101B (Voltage) & ACS712 (Current) -> Voltage Divider Circuit -> ADC
2. **Hardware Layer (FPGA):** Hardware-level ADC control and data packaging. Acts as an SPI Slave.
3. **Application Layer (Raspberry Pi):** Acts as an SPI Master. Receives raw data, applies conversion formulas, handles data visualization, and executes smart control algorithms.

## 📂 Repository Structure
The project is developed systematically, starting from basic module verification to full system integration:

* `01.SPI_Check/` : FPGA to Raspberry Pi SPI communication implementation and testing.
* `02.ADC_Check/` : ADC analog-to-digital signal conversion logic.
* `03.ADC_SPI_Check/` : Integration of ADC control and SPI data transmission modules.
* `04.CT_ADC_SPI_Check_Viewer/` : **(Core)** Integrated system reading ZMPT/ACS712 sensors with real-time waveform visualization (Python live oscilloscope).
* `Docs/` : Hardware datasheets, schematic designs, and technical documentation.

## 🚀 Roadmap & Milestones
- [x] Phase 1: SPI Communication setup between FPGA and Raspberry Pi
- [x] Phase 2: ADC interfacing and sensor calibration (Voltage/Current)
- [x] Phase 3: Real-time waveform visualization (Oscilloscope implemented)
- [ ] Phase 4: Power calculation algorithm (Vrms, Irms, Active Power)
- [ ] Phase 5: Appliance signature analysis and Smart Relay control
- [ ] Phase 6: Final enclosure design and system deployment

---
*Developed by Junyeong*
