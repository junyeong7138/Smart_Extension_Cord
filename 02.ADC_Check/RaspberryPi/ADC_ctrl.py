import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 100000
spi.mode = 0

R_LOAD = 330.0   # 330옴 저항

def read_mcp3202(channel=0):
    if channel == 0:
        cmd = [0b00000001, 0b10100000, 0b00000000]
    else:
        cmd = [0b00000001, 0b11100000, 0b00000000]

    resp = spi.xfer2(cmd)
    value = ((resp[1] & 0x0F) << 8) | resp[2]
    return value

try:
    while True:
        # CH0: 전압 채널
        val_ch0 = read_mcp3202(0)
        voltage_ch0 = val_ch0 * 3.3 / 4095

        # CH1: 전류 계산용 채널
        val_ch1 = read_mcp3202(1)
        voltage_ch1 = val_ch1 * 3.3 / 4095
        current_ch1 = voltage_ch1 / R_LOAD   # A 단위
        current_mA = current_ch1 * 1000      # mA 단위

        print(f"CH0 Voltage : {voltage_ch0:.3f} V")
        print(f"CH1 Voltage : {voltage_ch1:.3f} V")
        print(f"CH1 Current : {current_ch1:.6f} A  ({current_mA:.3f} mA)")
        print("-" * 40)

        time.sleep(0.5)

except KeyboardInterrupt:
    print("종료")

finally:
    spi.close()