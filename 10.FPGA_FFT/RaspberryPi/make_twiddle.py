import math

N = 64
HALF_N = N // 2

# 실수부와 허수부를 따로 저장하기 위해 두 개의 파일을 엽니다.
with open("twiddle_re.mem", "w") as f_re, open("twiddle_im.mem", "w") as f_im:
    for k in range(HALF_N):
        # 1. 각도 계산 (라디안)
        theta = -2.0 * math.pi * k / N
        
        # 2. 삼각함수 계산 (실수부: cos, 허수부: sin)
        re = math.cos(theta)
        im = math.sin(theta)
        
        # 3. 16비트 Q15 포맷으로 스케일링 (1.0 -> 32767)
        # 32767 = 2^15 - 1 (16비트 부호 있는 정수의 최댓값)
        re_q15 = int(round(re * 32767))
        im_q15 = int(round(im * 32767))
        
        # 4. 음수 처리 (2의 보수 변환)
        if re_q15 < 0:
            re_q15 = re_q15 + 65536
        if im_q15 < 0:
            im_q15 = im_q15 + 65536
            
        # 5. 16진수(Hex) 4자리 포맷으로 파일에 쓰기
        f_re.write(f"{re_q15:04x}\n")
        f_im.write(f"{im_q15:04x}\n")

print(f"✅ 16-bit Q15 Twiddle Factors 추출 완료! (N={N})")
print("- twiddle_re.mem (실수부)")
print("- twiddle_im.mem (허수부)")