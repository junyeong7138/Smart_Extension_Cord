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

    def set_mode(self, mode):
        self.current_mode = mode

    def get_mode(self):
        return self.current_mode

    def process_raw_mode(self):
        """1번 모드: 오실로스코프 스냅샷 데이터 수집 (1920Hz 동기화)"""
        samples_collected = 0
        while samples_collected < self.buffer_size:
            now = time.perf_counter()
            if now - self.last_sample_time >= 0.00052: 
                self.last_sample_time = now
                
                resp = self.spi.transfer([0x01, 0x00, 0x00, 0x00])
                raw_32bit = (resp[0] << 24) | (resp[1] << 16) | (resp[2] << 8) | resp[3]
                
                self.ch0_data[samples_collected] = ((raw_32bit >> 16) & 0x0FFF) - 2048
                self.ch1_data[samples_collected] = (raw_32bit & 0x0FFF) - 2048
                samples_collected += 1
                
        return self.ch0_data, self.ch1_data

    def process_fft_mode(self):
        """2번 모드: 하드웨어 FFT 결과 수집 및 크기 계산"""
        self.spi.transfer([0x01, 0x00, 0x00, 0x00]) # Sync 펄스
        self.spi.transfer([0x02, 0x00, 0x00, 0x00]) 

        new_fft_y = np.zeros(16)
        
        for i in range(64):
            resp = self.spi.transfer([0x02, 0x00, 0x00, 0x00])
            raw_32bit = (resp[0] << 24) | (resp[1] << 16) | (resp[2] << 8) | resp[3]
            
            re = (raw_32bit >> 16) & 0xFFFF
            im = raw_32bit & 0xFFFF
            
            # 2의 보수 부호 처리
            if re > 32767: re -= 65536
            if im > 32767: im -= 65536
            
            magnitude = np.sqrt(re**2 + im**2)
            
            # 1~16번 Bin (30Hz ~ 480Hz) 데이터만 추출
            if 1 <= i <= 16:
                new_fft_y[i-1] = magnitude
                
        return new_fft_y