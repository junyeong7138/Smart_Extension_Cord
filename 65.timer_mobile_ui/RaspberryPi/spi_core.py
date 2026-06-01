import spidev

class SPICore:
    def __init__(self, bus=0, device=0, max_speed_hz=2000000, mode=0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = max_speed_hz
        self.spi.mode = mode

    def transfer(self, data):
        """SPI로 데이터를 송수신합니다."""
        return self.spi.xfer2(data)

    def close(self):
        """SPI 포트를 안전하게 닫습니다."""
        self.spi.close()