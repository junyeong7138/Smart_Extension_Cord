import time
import numpy as np


class DSPEngine:
    def __init__(self, spi_core, buffer_size=150):
        self.spi = spi_core
        self.buffer_size = buffer_size

        # 데이터 버퍼
        self.ch0_data = np.zeros(self.buffer_size)
        self.ch1_data = np.zeros(self.buffer_size)

        # 상태 제어
        self.current_mode = 0x01
        self.last_sample_time = time.perf_counter()

        # -------------------------------------------------
        # SPI 초기 더미 읽기
        # 첫 프레임 첫 샘플에서 ch1 = -2048처럼 튀는 문제 완화
        # -------------------------------------------------
        for _ in range(3):
            try:
                self.spi.transfer([0x01, 0x00, 0x00, 0x00])
            except Exception:
                pass

    def set_mode(self, mode):
        self.current_mode = mode

    def get_mode(self):
        return self.current_mode

    def process_raw_mode(self):
        """
        1번 모드: 전압/전류 시간영역 RAW 데이터 수집

        반환:
            ch0_data    : CH0 centered ADC 배열
            ch1_data    : CH1 centered ADC 배열
            timestamps  : 각 샘플의 실제 timestamp
            fs_actual   : timestamp 기반 실측 sampling frequency
        """
        timestamps = np.zeros(self.buffer_size)
        samples_collected = 0

        while samples_collected < self.buffer_size:
            now = time.perf_counter()

            if now - self.last_sample_time >= 0.00052:
                self.last_sample_time = now

                resp = self.spi.transfer([0x01, 0x00, 0x00, 0x00])
                raw_32bit = (
                    (resp[0] << 24) |
                    (resp[1] << 16) |
                    (resp[2] << 8) |
                    resp[3]
                )

                ch0 = ((raw_32bit >> 16) & 0x0FFF) - 2048
                ch1 = (raw_32bit & 0x0FFF) - 2048

                self.ch0_data[samples_collected] = ch0
                self.ch1_data[samples_collected] = ch1
                timestamps[samples_collected] = time.time()

                samples_collected += 1

        # timestamp 기반 실제 fs 계산
        dt = np.diff(timestamps)
        dt = dt[dt > 0]

        if len(dt) > 0:
            fs_actual = float(1.0 / np.mean(dt))
        else:
            fs_actual = 0.0

        return (
            self.ch0_data.copy(),
            self.ch1_data.copy(),
            timestamps.copy(),
            fs_actual
        )

    def process_fft_mode(self):
        """
        2번 모드: FPGA FFT 결과 수집 및 magnitude 계산

        반환:
            new_fft_y : 30Hz ~ 480Hz, 16개 bin magnitude
        """
        # Sync / FFT mode 요청
        self.spi.transfer([0x01, 0x00, 0x00, 0x00])
        self.spi.transfer([0x02, 0x00, 0x00, 0x00])

        new_fft_y = np.zeros(16)

        for i in range(64):
            resp = self.spi.transfer([0x02, 0x00, 0x00, 0x00])
            raw_32bit = (
                (resp[0] << 24) |
                (resp[1] << 16) |
                (resp[2] << 8) |
                resp[3]
            )

            re = (raw_32bit >> 16) & 0xFFFF
            im = raw_32bit & 0xFFFF

            # 2의 보수 부호 처리
            if re > 32767:
                re -= 65536
            if im > 32767:
                im -= 65536

            magnitude = np.sqrt(re ** 2 + im ** 2)

            # 1~16번 bin만 사용
            # 30Hz, 60Hz, ... , 480Hz
            if 1 <= i <= 16:
                new_fft_y[i - 1] = magnitude

        return new_fft_y