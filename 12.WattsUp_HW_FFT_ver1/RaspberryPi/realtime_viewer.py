import spidev
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ==========================================
# 1. SPI 통신 및 데이터 세팅
# ==========================================
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 2000000 
spi.mode = 0

current_mode = 0x01
BUFFER_SIZE = 150
ch0_data = np.zeros(BUFFER_SIZE)
ch1_data = np.zeros(BUFFER_SIZE)

# 💡 FFT 주파수 배열 (1번 Bin = 30Hz 부터 16번 Bin = 480Hz 까지만 그립니다)
# 60, 180, 300, 420Hz가 완벽하게 이 범위 안에 들어갑니다.
fft_x_hz = np.arange(1, 17) * 30.0  
fft_y = np.zeros(16)

# ==========================================
# 2. 프로페셔널 다크모드 UI 세팅
# ==========================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
fig.canvas.manager.set_window_title('WattsUp Professional DSP Monitor')
fig.patch.set_facecolor('#1e1e1e')

# [상단] 오실로스코프
line_ch0, = ax1.plot(ch0_data, label='Voltage (CH0 - PT)', color='magenta', linewidth=2)
line_ch1, = ax1.plot(ch1_data, label='Current (CH1 - CT)', color='cyan', linewidth=2)
ax1.set_ylim(-2048, 2048)
ax1.set_xlim(0, BUFFER_SIZE)
ax1.set_title("Mode 1: Real-time Oscilloscope (Press '1')", color='white')
ax1.legend(loc='upper right')
ax1.grid(True, linestyle='--', alpha=0.3)
ax1.set_facecolor('black')

# [하단] 주파수 스펙트럼 분석기 
bars = ax2.bar(fft_x_hz, fft_y, color='lime', width=15)
ax2.set_xlim(0, 500)
ax2.set_ylim(0, 10000) # 💡 하드웨어에서 4로 나누었으므로 Y축 최댓값을 낮췄습니다.
ax2.set_title("Mode 2: Harmonic Spectrum (Press '2')", color='white')
ax2.set_facecolor('black')

# 💡 X축 눈금(Tick)을 원하는 고조파 주파수에 딱 맞게 강제 고정합니다!
target_freqs = [60, 180, 300, 420]
ax2.set_xticks(target_freqs)
ax2.set_xticklabels([f"{f}Hz" for f in target_freqs], color='yellow', fontweight='bold', fontsize=12)
ax2.grid(True, axis='x', color='yellow', linestyle=':', alpha=0.5) # 타겟 주파수에 세로줄 표시
ax2.grid(True, axis='y', linestyle='--', alpha=0.3)

for ax in [ax1, ax2]:
    ax.tick_params(colors='white')
    for spine in ax.spines.values(): spine.set_edgecolor('gray')

def on_key(event):
    global current_mode
    if event.key == '1':
        current_mode = 0x01
        ax1.set_alpha(1.0); ax2.set_alpha(0.2)
    elif event.key == '2':
        current_mode = 0x02
        ax1.set_alpha(0.2); ax2.set_alpha(1.0)

fig.canvas.mpl_connect('key_press_event', on_key)
ax1.set_alpha(1.0); ax2.set_alpha(0.2)

last_sample_time = time.perf_counter()

# ==========================================
# 3. 실시간 업데이트 로직
# ==========================================
def update(frame):
    global ch0_data, ch1_data, last_sample_time

    if current_mode == 0x01:
        samples_collected = 0
        while samples_collected < BUFFER_SIZE:
            now = time.perf_counter()
            if now - last_sample_time >= 0.00052: 
                last_sample_time = now
                
                resp = spi.xfer2([0x01, 0x00, 0x00, 0x00])
                raw_32bit = (resp[0] << 24) | (resp[1] << 16) | (resp[2] << 8) | resp[3]
                
                ch0_data[samples_collected] = ((raw_32bit >> 16) & 0x0FFF) - 2048
                ch1_data[samples_collected] = (raw_32bit & 0x0FFF) - 2048
                samples_collected += 1
                
        line_ch0.set_ydata(ch0_data)
        line_ch1.set_ydata(ch1_data)
        return line_ch0, line_ch1

    elif current_mode == 0x02:
        spi.xfer2([0x01, 0x00, 0x00, 0x00]) 
        spi.xfer2([0x02, 0x00, 0x00, 0x00]) 

        new_fft_y = np.zeros(16)
        
        for i in range(64):
            resp = spi.xfer2([0x02, 0x00, 0x00, 0x00])
            raw_32bit = (resp[0] << 24) | (resp[1] << 16) | (resp[2] << 8) | resp[3]
            
            re = (raw_32bit >> 16) & 0xFFFF
            im = raw_32bit & 0xFFFF
            if re > 32767: re -= 65536
            if im > 32767: im -= 65536
            
            magnitude = np.sqrt(re**2 + im**2)
            
            if 1 <= i <= 16:
                new_fft_y[i-1] = magnitude
                
        for bar, h in zip(bars, new_fft_y):
            bar.set_height(h)
            
        # 💡 [신규 추가] Y축 자동 스케일링 (가전기기 소비 전력에 따라 동적 조절)
        max_val = np.max(new_fft_y)
        if max_val > 100:  # 노이즈일 때는 줌인하지 않음
            ax2.set_ylim(0, max_val * 1.2) # 가장 높은 막대보다 20% 높게 설정
        else:
            ax2.set_ylim(0, 1000)
            
        return bars

ani = animation.FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)
plt.show()