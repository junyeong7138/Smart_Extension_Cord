import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
spi.mode = 0

def read_mcp3202(channel=0):
    if channel == 0:
        cmd = [0b00000001, 0b10100000, 0b00000000]
    else:
        cmd = [0b00000001, 0b11100000, 0b00000000]

    resp = spi.xfer2(cmd)

    value = ((resp[1] & 0x0F) << 8) | resp[2]
    return value

while True:
    val = read_mcp3202(0)
    voltage = val * 3.3 / 4095
    print(f"ADC: {val:4d}   Voltage: {voltage:.3f} V")
    time.sleep(0.5)