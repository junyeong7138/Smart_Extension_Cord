import spidev
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# --- 1. 하드웨어 설정 ---
spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0
spi.max_speed_hz = 1000000  # 통신 속도를 올려서 파형을 부드럽게 잡습니다.

DIVIDER_RATIO = (2.0 + 3.3) / 3.3 
ACS_OFFSET_V = 2.5       
ACS_SENSITIVITY = 0.185  

# --- 2. 그래프 데이터 저장소 (Deque) ---
# MAX_POINTS 개수만큼만 데이터를 유지하고, 넘치면 오래된 것부터 버립니다 (스크롤 효과)
MAX_POINTS = 100
x_data = deque(maxlen=MAX_POINTS)
v_data = deque(maxlen=MAX_POINTS)
i_data = deque(maxlen=MAX_POINTS)

# --- 3. 그래프 창(Window) 초기 설정 ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
fig.canvas.manager.set_window_title('WattsUp Live Oscilloscope')

# 위쪽: 전압 그래프
line_v, = ax1.plot([], [], lw=2, color='blue')
ax1.set_title('ZMPT101B Voltage (V)')
ax1.set_ylim(0, 5)  # 전압 Y축 범위 (필요시 수정)
ax1.grid(True)

# 아래쪽: 전류 그래프
line_i, = ax2.plot([], [], lw=2, color='red')
ax2.set_title('ACS712 Current (mA)')
ax2.set_ylim(-1000, 1000)  # 전류 Y축 범위 (노이즈가 심하면 늘리세요)
ax2.grid(True)

sample_count = 0

def init():
    """애니메이션 시작 전 초기화 함수"""
    line_v.set_data([], [])
    line_i.set_data([], [])
    return line_v, line_i

def update(frame):
    """지정된 시간(ms)마다 반복 실행되며 데이터를 읽고 화면을 갱신하는 함수"""
    global sample_count
    
    # FPGA로부터 데이터 수신
    resp = spi.xfer2([0x00, 0x00, 0x00, 0x00])

    ch0 = ((resp[0] << 8) | resp[1]) & 0x0FFF
    ch1 = ((resp[2] << 8) | resp[3]) & 0x0FFF

    # 공식 계산
    real_voltage_ch0 = (ch0 * 3.3 / 4095.0) * DIVIDER_RATIO
    real_voltage_ch1 = (ch1 * 3.3 / 4095.0) * DIVIDER_RATIO
    current_mA = ((real_voltage_ch1 - ACS_OFFSET_V) / ACS_SENSITIVITY) * 1000

    # 데이터 큐에 추가
    x_data.append(sample_count)
    v_data.append(real_voltage_ch0)
    i_data.append(current_mA)
    sample_count += 1

    # 화면이 왼쪽으로 흘러가도록 X축 범위 지속 업데이트
    ax1.set_xlim(max(0, sample_count - MAX_POINTS), max(sample_count, MAX_POINTS))
    ax2.set_xlim(max(0, sample_count - MAX_POINTS), max(sample_count, MAX_POINTS))

    # 그래프 선 그리기
    line_v.set_data(x_data, v_data)
    line_i.set_data(x_data, i_data)

    return line_v, line_i

print("실시간 파형 창을 띄웁니다! (창을 닫으면 프로그램이 종료됩니다)")

try:
    # interval=20: 20ms(0.02초)마다 화면 갱신 (더 부드럽게 보려면 10으로 낮추세요)
    ani = animation.FuncAnimation(fig, update, init_func=init, blit=False, interval=20)
    plt.tight_layout()
    plt.show()  # 여기서 팝업 창이 뜹니다!

except KeyboardInterrupt:
    print("\n시스템을 안전하게 종료합니다.")

finally:
    spi.close()
    