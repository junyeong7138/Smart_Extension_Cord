# FPGA Button Detection Project

This project demonstrates a hardware-software integration where physical button presses on an FPGA are detected and transmitted to a Raspberry Pi for real-time console output.

## Overview
The system monitors four tactile switches (Button 0 to 3) on the FPGA. When a button is pressed, the FPGA identifies the button index and sends this information to the Raspberry Pi via SPI (Serial Peripheral Interface) communication.

## Key Features
- **FPGA Logic**: Implements button debouncing and an SPI Slave module in Verilog.
- **Communication**: Uses high-speed SPI to ensure low-latency data transfer between FPGA and Raspberry Pi.
- **Raspberry Pi Integration**: A Python-based script processes the incoming SPI packets and displays the active button index on the terminal.

## Hardware Components
- **FPGA**: [DE2-115, e.g., Cyclone IV]
- **Processor**: Raspberry Pi [4 Model B]
- **Interface**: SPI Pins (MOSI, MISO, SCLK, CS)

## How to Run
1. Synthesize and program the FPGA with the provided bitstream.
2. Ensure the SPI interface is enabled on your Raspberry Pi.
3. Run the monitoring script:
   ```bash
   python3 button_monitor.py
