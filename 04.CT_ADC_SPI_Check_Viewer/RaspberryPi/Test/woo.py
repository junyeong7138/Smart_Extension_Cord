import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0
spi.max_speed_hz = 100000

R_LOAD = 330.0

try:
    print("FPGA로부터 CH0 / CH1 데이터 수신 시작...")

    while True:
        resp = spi.xfer2([0x00, 0x00, 0x00, 0x00])

        ch0 = ((resp[0] << 8) | resp[1]) & 0x0FFF
        ch1 = ((resp[2] << 8) | resp[3]) & 0x0FFF

        voltage_ch0 = ch0 * 3.3 / 4095.0
        voltage_ch1 = ch1 * 3.3 / 4095.0
        current_ch1 = voltage_ch1 / R_LOAD
        current_mA = current_ch1 * 1000

        print(f"RAW: {resp}")
        print(f"CH0 ADC: {ch0:4d} | CH0 Voltage: {voltage_ch0:.3f} V")
        print(f"CH1 ADC: {ch1:4d} | CH1 Voltage: {voltage_ch1:.3f} V | CH1 Current: {current_mA:.3f} mA")
        print("-" * 60)

        time.sleep(0.5)

except KeyboardInterrupt:
    print("종료")

finally:
    spi.close()