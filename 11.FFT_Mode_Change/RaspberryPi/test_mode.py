import spidev
import time

# SPI 설정
spi = spidev.SpiDev()
spi.open(0, 0) # bus 0, device 0
spi.max_speed_hz = 2000000 # 2MHz
spi.mode = 0

print("========================================")
print(" 🚀 WattsUp SPI 모드 전환 테스트 🚀 ")
print("========================================")
print("키보드로 모드를 선택하고 Enter를 누르세요.")
print(" [1] RAW 모드 (오실로스코프용 데이터)")
print(" [2] FFT 모드 (BEEFCAFE 가짜 데이터)")
print(" [q] 테스트 종료")
print("========================================\n")

# 초기 커맨드는 RAW 모드로 설정
current_cmd = [0x01, 0x00, 0x00, 0x00] 

try:
    while True:
        user_input = input("\n모드 선택 (1/2/q) >> ")
        
        if user_input == 'q':
            break
        elif user_input == '1':
            print("\n명령 송신: [RAW 데이터 모드 전환 (0x01)]")
            current_cmd = [0x01, 0x00, 0x00, 0x00]
        elif user_input == '2':
            print("\n명령 송신: [FFT 분석 모드 전환 (0x02)]")
            current_cmd = [0x02, 0x00, 0x00, 0x00]
        else:
            print("잘못된 입력입니다. 1, 2, q 중에서 선택하세요.")
            continue

        print("-" * 40)
        # 5번 연속으로 데이터를 읽어서 출력
        for i in range(5):
            # [수정된 부분] 원본이 덮어씌워지는 것을 막기 위해 리스트 복사본([:])을 생성
            cmd_to_send = current_cmd[:] 
            resp = spi.xfer2(cmd_to_send)

            # 4바이트(32비트) 배열을 16진수 값으로 합치기
            raw_32bit = (resp[0] << 24) | (resp[1] << 16) | (resp[2] << 8) | resp[3]

            if current_cmd[0] == 0x01:
                # RAW 모드일 경우: CH0(상위 16), CH1(하위 16) 분리하여 출력
                ch0 = (raw_32bit >> 16) & 0x0FFF
                ch1 = raw_32bit & 0x0FFF
                print(f"[{i+1}] [RAW] 수신 Hex: 0x{raw_32bit:08X}  -> CH0: {ch0:4d}, CH1: {ch1:4d}")
            else:
                # FFT 모드일 경우: BEEFCAFE 글자가 정상적으로 들어오는지 확인
                print(f"[{i+1}] [FFT] 수신 Hex: 0x{raw_32bit:08X}")
                
            time.sleep(0.05) # 너무 빠르지 않게 0.05초 대기
        print("-" * 40)

except KeyboardInterrupt:
    pass
finally:
    print("\n테스트를 종료하고 SPI 포트를 닫습니다.")
    spi.close()