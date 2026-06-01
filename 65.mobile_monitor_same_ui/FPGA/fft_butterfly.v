`timescale 1ns / 1ps

module fft_butterfly (
    // 입력 A (실수부, 허수부)
    input  wire signed [15:0] a_re,
    input  wire signed [15:0] a_im,
    // 입력 B (실수부, 허수부)
    input  wire signed [15:0] b_re,
    input  wire signed [15:0] b_im,
    // Twiddle Factor W (사인/코사인 롬에서 읽어온 값)
    input  wire signed [15:0] w_re,
    input  wire signed [15:0] w_im,
    
    // 출력 A'와 B'
    output reg  signed [15:0] out_a_re,
    output reg  signed [15:0] out_a_im,
    output reg  signed [15:0] out_b_re,
    output reg  signed [15:0] out_b_im
);

    // 1. 복소수 곱셈: W * B
    // (W_r + jW_i) * (B_r + jB_i) = (W_r*B_r - W_i*B_i) + j(W_r*B_i + W_i*B_r)
    wire signed [31:0] mult_re1 = b_re * w_re;
    wire signed [31:0] mult_re2 = b_im * w_im;
    wire signed [31:0] mult_im1 = b_re * w_im;
    wire signed [31:0] mult_im2 = b_im * w_re;

    wire signed [31:0] bw_re_full = mult_re1 - mult_re2;
    wire signed [31:0] bw_im_full = mult_im1 + mult_im2;

    // 2. Q15 포맷 스케일링 (32비트 결과를 다시 16비트로 축소)
    // 두 개의 Q15를 곱하면 소수점이 30번째 비트에 위치하게 되므로 [30:15]를 잘라냅니다.
    wire signed [15:0] bw_re = bw_re_full[30:15];
    wire signed [15:0] bw_im = bw_im_full[30:15];

    // 3. 덧셈 및 뺄셈 (나비 구조)
    always @(*) begin
        // A' = A + (W*B)
        out_a_re = a_re + bw_re;
        out_a_im = a_im + bw_im;
        
        // B' = A - (W*B)
        out_b_re = a_re - bw_re;
        out_b_im = a_im - bw_im;
    end

endmodule