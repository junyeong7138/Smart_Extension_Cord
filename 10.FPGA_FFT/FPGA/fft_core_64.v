module fft_core_64(
    input  wire clk,
    input  wire rst_n,
    
    // ADC에서 들어오는 센서 데이터
    input  wire [11:0] adc_data,
    input  wire adc_valid,
    
    // 라즈베리파이(WattsUp.v)로 나가는 결과
    output reg  [31:0] fft_result_data,
    output reg  fft_done
);

    // 상태 정의 (State Machine)
    localparam IDLE       = 3'd0;
    localparam LOAD       = 3'd1; // ADC 데이터 64개 수집
    localparam CALC_FFT   = 3'd2; // Butterfly 연산 (Stage 1~6)
    localparam CALC_MAG   = 3'd3; // 실수/허수로부터 크기(Magnitude) 계산
    localparam DONE       = 3'd4; // 전송 준비 완료

    reg [2:0] state;
    reg [6:0] sample_cnt; // 0 ~ 63 카운트
    reg [2:0] stage_cnt;  // 1 ~ 6 스테이지 카운트

    // =========================================================
    // 1. 메모리(RAM & ROM) 선언
    // =========================================================
    // 센서 데이터를 저장할 64칸짜리 RAM (실수부, 허수부)
    reg signed [15:0] ram_re [0:63];
    reg signed [15:0] ram_im [0:63];

    // 파이썬에서 추출한 Twiddle Factor를 담을 32칸짜리 ROM
    reg signed [15:0] rom_tw_re [0:31];
    reg signed [15:0] rom_tw_im [0:31];

    // 합성이 시작될 때 딱 한 번 .mem 파일을 읽어서 ROM에 굽습니다.
    initial begin
        $readmemh("twiddle_re.mem", rom_tw_re);
        $readmemh("twiddle_im.mem", rom_tw_im);
    end

    // =========================================================
    // 2. 비트 역순(Bit-Reversal) 주소 생성기
    // =========================================================
    // sample_cnt(0~63)은 6비트입니다. 이 순서를 거꾸로 뒤집어줍니다.
    wire [5:0] bit_reversed_addr;
    assign bit_reversed_addr = {sample_cnt[0], sample_cnt[1], sample_cnt[2], 
                                sample_cnt[3], sample_cnt[4], sample_cnt[5]};

    // (선택 사항) ADC 12비트 데이터를 16비트 Q15에 맞게 위치를 조정합니다.
    // 12비트 센서값을 최상위 부호 비트 바로 아래로 끌어올립니다.
    wire signed [15:0] adc_q15 = {1'b0, adc_data, 3'b000}; 

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            sample_cnt <= 0;
            stage_cnt <= 0;
            fft_done <= 0;
            fft_result_data <= 32'h0;
        end else begin
            case (state)
                IDLE: begin
                    fft_done <= 0;
                    sample_cnt <= 0;
                    if (adc_valid) state <= LOAD;
                end
                
                LOAD: begin
                    if (adc_valid) begin
                        // 뒤집힌 주소(bit_reversed_addr)에 데이터 저장!
                        ram_re[bit_reversed_addr] <= adc_q15;
                        ram_im[bit_reversed_addr] <= 16'd0; // 처음엔 허수부가 없으므로 0
                        
                        if (sample_cnt == 63) begin
                            state <= CALC_FFT;
                            sample_cnt <= 0;
                            stage_cnt <= 1;
                        end else begin
                            sample_cnt <= sample_cnt + 1;
                        end
                    end
                end
                
                CALC_FFT: begin
                    // 여기서 fft_butterfly.v 모듈을 인스턴스화하여 메모리 값을 읽고 씁니다.
                    // Stage 1부터 6까지 반복하며 메모리를 업데이트합니다.
                    
                    // 연산이 모두 끝났다고 가정
                    // if (stage_cnt == 6 && stage_완료) begin
                    state <= CALC_MAG; 
                end
                
                CALC_MAG: begin
                    // 복소수 결과를 라즈베리파이가 보기 편하게 절댓값 크기(Magnitude)로 변환
                    // Mag = sqrt(Re^2 + Im^2) (하드웨어에서는 근사치 알고리즘 사용)
                    
                    // 완료 후 최종 데이터를 레지스터에 올림
                    fft_result_data <= 32'hBEEF_CAFE; // (테스트용 가짜 FFT 완료 데이터)
                    state <= DONE;
                end
                
                DONE: begin
                    fft_done <= 1; // 라즈베리파이에게 "가져가라!"고 신호
                    state <= IDLE;
                end
            endcase
        end
    end

endmodule