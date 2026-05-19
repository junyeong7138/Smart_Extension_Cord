import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class DashboardUI:
    def __init__(self, dsp_engine):
        self.engine = dsp_engine
        self.buffer_size = self.engine.buffer_size
        
        # X축 주파수 배열 (30Hz ~ 480Hz)
        self.fft_x_hz = np.arange(1, 17) * 30.0  

        # UI 창 세팅
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.fig.canvas.manager.set_window_title('WattsUp Professional DSP Monitor')
        self.fig.patch.set_facecolor('#1e1e1e')

        # [상단] 오실로스코프 세팅
        self.line_ch0, = self.ax1.plot(np.zeros(self.buffer_size), label='Voltage (CH0 - PT)', color='magenta', linewidth=2)
        self.line_ch1, = self.ax1.plot(np.zeros(self.buffer_size), label='Current (CH1 - CT)', color='cyan', linewidth=2)
        self.ax1.set_ylim(-2048, 2048)
        self.ax1.set_xlim(0, self.buffer_size)
        self.ax1.set_title("Mode 1: Real-time Oscilloscope (Press '1')", color='white')
        self.ax1.legend(loc='upper right')
        self.ax1.grid(True, linestyle='--', alpha=0.3)
        self.ax1.set_facecolor('black')

        # [하단] 스펙트럼 분석기 세팅
        self.bars = self.ax2.bar(self.fft_x_hz, np.zeros(16), color='lime', width=15)
        self.ax2.set_xlim(0, 500)
        self.ax2.set_ylim(0, 10000) 
        self.ax2.set_title("Mode 2: Harmonic Spectrum (Press '2')", color='white')
        self.ax2.set_facecolor('black')

        # X축 눈금 고정 (고조파 타겟)
        target_freqs = [60, 180, 300, 420]
        self.ax2.set_xticks(target_freqs)
        self.ax2.set_xticklabels([f"{f}Hz" for f in target_freqs], color='yellow', fontweight='bold', fontsize=12)
        self.ax2.grid(True, axis='x', color='yellow', linestyle=':', alpha=0.5) 
        self.ax2.grid(True, axis='y', linestyle='--', alpha=0.3)

        for ax in [self.ax1, self.ax2]:
            ax.tick_params(colors='white')
            for spine in ax.spines.values(): spine.set_edgecolor('gray')

        # 이벤트 연결
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.ax1.set_alpha(1.0)
        self.ax2.set_alpha(0.2)

    def on_key(self, event):
        """키보드 입력 이벤트 처리"""
        if event.key == '1':
            self.engine.set_mode(0x01)
            self.ax1.set_alpha(1.0); self.ax2.set_alpha(0.2)
        elif event.key == '2':
            self.engine.set_mode(0x02)
            self.ax1.set_alpha(0.2); self.ax2.set_alpha(1.0)

    def update_frame(self, frame):
        """애니메이션 프레임 업데이트"""
        current_mode = self.engine.get_mode()

        if current_mode == 0x01:
            ch0, ch1 = self.engine.process_raw_mode()
            self.line_ch0.set_ydata(ch0)
            self.line_ch1.set_ydata(ch1)
            return self.line_ch0, self.line_ch1

        elif current_mode == 0x02:
            new_fft_y = self.engine.process_fft_mode()
            
            for bar, h in zip(self.bars, new_fft_y):
                bar.set_height(h)
                
            # Y축 자동 스케일링
            max_val = np.max(new_fft_y)
            if max_val > 100:  
                self.ax2.set_ylim(0, max_val * 1.2) 
            else:
                self.ax2.set_ylim(0, 1000)
                
            return self.bars

    def start(self):
        """애니메이션 실행"""
        self.ani = animation.FuncAnimation(
            self.fig, self.update_frame, interval=50, blit=False, cache_frame_data=False
        )
        plt.show()