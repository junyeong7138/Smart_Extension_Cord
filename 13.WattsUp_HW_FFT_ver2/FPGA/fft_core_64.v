module fft_core_64(
    input  wire clk,
    input  wire rst_n,
    
    // ADC에서 들어오는 센서 데이터
    input  wire [11:0] adc_data,
    input  wire adc_valid,

    // [신규 추가] WattsUp.v에서 현재 모드와 통신 상태를 받아옴
    input  wire [7:0] sys_mode,   
    input  wire cmd_valid,        
    
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

    // (참고) 실제 구현 시 여기에 64개의 데이터를 담을 Dual-Port RAM(배열)과
    // Twiddle Factor(사인/코사인)를 담은 ROM을 선언해야 합니다.
    // =========================================================
    // 1. 메모리(RAM & ROM) 선언
    // =========================================================
    // 센서 데이터를 저장할 64칸짜리 RAM (실수부, 허수부)
    reg signed [15:0] ram_re [0:63];
    reg signed [15:0] ram_im [0:63];

    // =========================================================
    // [신규 추가] 라즈베리파이가 안전하게 읽어갈 출력 전용 버퍼 (더블 버퍼링)
    // =========================================================
    reg signed [15:0] out_re [0:63];
    reg signed [15:0] out_im [0:63];
    reg [5:0] copy_cnt;

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

    // [기존 코드 삭제]
    // wire signed [15:0] adc_q15 = {1'b0, adc_data, 3'b000}; 

    // =========================================================
    // [수정된 코드] 데이터 전처리
    // =========================================================
    // 1. DC 오프셋 제거: 0~4095를 -2048~+2047로 만듭니다.
    wire signed [12:0] adc_centered = {1'b0, adc_data} - 13'd2048;
    
    // 2. 진폭 복구: CT 센서(전류)는 진폭이 작으므로 4로 나누지 않고 그대로 넣습니다!
    wire signed [15:0] adc_q15 = {{3{adc_centered[12]}}, adc_centered};

    // =========================================================
    // [신규 추가] 나비 연산 스케줄링용 카운터 및 레지스터
    // =========================================================
    reg [1:0] bf_state;        // 나비 연산 세부 상태 (0:주소세팅, 1:대기, 2:계산&저장)
    reg [5:0] element_cnt;     // 그룹 내 원소 카운트
    reg [5:0] grp_start;       // 그룹의 시작 주소
    reg [5:0] addr_a, addr_b;  // RAM에서 읽고 쓸 주소 A, B
    reg [4:0] addr_w;          // ROM에서 읽어올 Twiddle Factor 주소

    wire [5:0] span = 1 << (stage_cnt - 1); // 나비 연산 간격 (1, 2, 4, 8, 16, 32)

    // =========================================================
    // [신규 추가] 나비 연산기(Butterfly Unit) 인스턴스
    // =========================================================
    wire signed [15:0] out_a_re, out_a_im, out_b_re, out_b_im;

    fft_butterfly u_bf (
        // RAM과 ROM에서 주소에 맞게 데이터를 즉시 읽어서 넣습니다.
        .a_re(ram_re[addr_a]), .a_im(ram_im[addr_a]),
        .b_re(ram_re[addr_b]), .b_im(ram_im[addr_b]),
        .w_re(rom_tw_re[addr_w]), .w_im(rom_tw_im[addr_w]),
        // 계산된 결과
        .out_a_re(out_a_re), .out_a_im(out_a_im),
        .out_b_re(out_b_re), .out_b_im(out_b_im)
    );

    // =========================================================

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            sample_cnt <= 0;
            stage_cnt <= 0;
            fft_done <= 0;
            copy_cnt <= 6'd0; // [신규 추가]
        end else begin
            case (state)
                IDLE: begin
                    fft_done <= 0;
                    sample_cnt <= 0;
                    if (adc_valid) state <= LOAD;
                end
                
                LOAD: begin
                    if (adc_valid) begin
                        // 뒤집힌 주소(bit_reversed_addr)에 센서 데이터 저장!
                        ram_re[bit_reversed_addr] <= adc_q15;
                        ram_im[bit_reversed_addr] <= 16'd0; // 처음엔 허수부가 없으므로 0
                        
                        // (기존 LOAD 상태 내부의 완료 조건문)
                        if (sample_cnt == 63) begin
                            state <= CALC_FFT;
                            sample_cnt <= 0;
                            stage_cnt <= 1;
                            // [추가] 나비 연산 카운터 초기화
                            bf_state <= 2'd0;
                            element_cnt <= 6'd0;
                            grp_start <= 6'd0;
                        end else begin
                            sample_cnt <= sample_cnt + 1;
                        end
                    end
                end
                
                CALC_FFT: begin
                    if (stage_cnt > 6) begin
                        // 6스테이지가 모두 끝나면 크기 계산으로 넘어갑니다.
                        state <= CALC_MAG; 
                    end else begin
                        case (bf_state)
                            2'd0: begin // [Step 1] 주소 세팅 (Address Generation)
                                addr_a <= grp_start + element_cnt;
                                addr_b <= grp_start + element_cnt + span;
                                // Twiddle Factor 주소 = 원소번호 * (32 / span)
                                addr_w <= element_cnt << (6 - stage_cnt); 
                                
                                bf_state <= 2'd1;
                            end
                            
                            2'd1: begin // [Step 2] 메모리 읽기 대기 (RAM/ROM Read Latency)
                                // 블록 램(BRAM)에서 데이터를 안전하게 꺼내올 1클럭의 시간을 줍니다.
                                bf_state <= 2'd2;
                            end
                            
                            2'd2: begin // [Step 3] 결과 저장 및 카운터 증가 (Write & Increment)
                                // 조합회로인 u_bf가 계산해낸 A', B' 값을 RAM의 원래 자리에 덮어씁니다. (In-place)
                                ram_re[addr_a] <= out_a_re;
                                ram_im[addr_a] <= out_a_im;
                                ram_re[addr_b] <= out_b_re;
                                ram_im[addr_b] <= out_b_im;

                                // 다음 데이터를 위한 카운터 계산 로직
                                if (element_cnt == span - 1) begin
                                    // 한 그룹이 끝났으므로 다음 그룹으로 이동
                                    element_cnt <= 6'd0;
                                    if (grp_start + (span << 1) >= 64) begin
                                        // 64개를 다 돌았으면 현재 스테이지 종료 -> 다음 스테이지로!
                                        grp_start <= 6'd0;
                                        stage_cnt <= stage_cnt + 1;
                                    end else begin
                                        // 다음 그룹의 시작 주소로 점프
                                        grp_start <= grp_start + (span << 1);
                                    end
                                end else begin
                                    // 아직 그룹 내 원소가 남았으면 다음 원소로
                                    element_cnt <= element_cnt + 1;
                                end

                                bf_state <= 2'd0; // 다시 주소 세팅으로 루프
                            end
                        endcase
                    end
                end
                
                CALC_MAG: begin
                    // FFT 연산이 완벽하게 끝난 결과를 '출력 전용 버퍼'로 복사합니다.
                    out_re[copy_cnt] <= ram_re[copy_cnt];
                    out_im[copy_cnt] <= ram_im[copy_cnt];
                    
                    if (copy_cnt == 63) begin
                        state <= DONE;
                        copy_cnt <= 6'd0;
                    end else begin
                        copy_cnt <= copy_cnt + 1;
                    end
                end
                
                DONE: begin
                    fft_done <= 1; // 라즈베리파이에게 "가져가라!"고 신호
                    state <= IDLE;
                end
            endcase
        end
    end

    // =========================================================
    // [신규 추가] 라즈베리파이 전송용 메모리 읽기 포인터
    // =========================================================
    reg [5:0] read_ptr;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            read_ptr <= 6'd0;
            fft_result_data <= 32'd0;
        end else begin
            // RAW 모드일 때는 포인터를 0으로 초기화 대기
            if (sys_mode == 8'h01) begin
                read_ptr <= 6'd0;
            end 
            // FFT 모드일 때, 라즈베리파이가 1번 읽어갈 때(cmd_valid)마다 다음 칸으로 이동
            else if (sys_mode == 8'h02 && cmd_valid) begin
                read_ptr <= read_ptr + 1;
            end
            
            // 현재 포인터가 가리키는 메모리 값을 32비트로 묶어서 출력 (상위: 실수, 하위: 허수)
            // [기존 코드] fft_result_data <= {ram_re[read_ptr], ram_im[read_ptr]};
            
            // [수정된 코드] 연산 중인 메모리 대신, 안전하게 완성된 출력 버퍼를 읽습니다!
            fft_result_data <= {out_re[read_ptr], out_im[read_ptr]};
        end
    end

    // (참고) 기존 CALC_MAG 상태의 BEEFCAFE 부분은 지우셔도 되고 놔두셔도 됩니다. 
    // 이제 fft_result_data는 위 always 블록에서 덮어씌워집니다.

endmodule