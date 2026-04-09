import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)          # bus 0, device 0
spi.mode = 0
spi.max_speed_hz = 500000

last_value = None
first_read = True

try:
    print("SPI 수신 대기 중...")

    while True:
        value = spi.xfer2([0x00])[0]

        # 처음 읽은 값은 무시하고 기준값으로만 저장
        if first_read:
            last_value = value
            first_read = False
            time.sleep(0.1)
            continue

        # 값이 바뀌었을 때만 출력
        if value != last_value:
            if value == 161:
                print("0번 버튼")
            elif value == 178:
                print("1번 버튼")
            elif value == 195:
                print("2번 버튼")
            elif value == 212:
                print("3번 버튼")
            else:
                print("SPI 수신 대기 중...")

            last_value = value

        time.sleep(0.1)

except KeyboardInterrupt:
    print("종료")

finally:
    spi.close()
