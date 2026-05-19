module WattsUp(
    input CLOCK_50,
    input [3:0] KEY,

    // Raspberry Pi <-> FPGA
    input  RPI_SPI_SCLK,
    input  RPI_SPI_CS_N,
    input  RPI_SPI_MOSI,
    output RPI_SPI_MISO,

    // ADC(MCP3202) <-> FPGA
    output ADC_CS_N,
    output ADC_SCLK,
    output ADC_MOSI,
    input  ADC_MISO,

    output temp_wire0,
    output temp_wire1,
    output LED0,
    output LED1,

    input sw0,
    input sw1
);

    assign LED0 = sw0;
    assign LED1 = sw1;
    assign temp_wire0 = LED0;
    assign temp_wire1 = LED1;

    wire rst_n = KEY[0];

    // 1) ADC 측정 주기 생성
    reg [15:0] timer_cnt;
    reg adc_start;

    always @(posedge CLOCK_50 or negedge rst_n) begin
        if (!rst_n) begin
            timer_cnt  <= 16'd0;
            adc_start  <= 1'b0;
        end else begin
            if (timer_cnt == 16'd50000) begin
                timer_cnt <= 16'd0;
                adc_start <= 1'b1;   
            end else begin
                timer_cnt <= timer_cnt + 16'd1;
                adc_start <= 1'b0;
            end
        end
    end

    // 2) ADC 읽기 관련 내부 신호
    wire [11:0] w_adc_data;
    wire        w_adc_valid;
    reg         ch_sel_reg;
    reg [11:0]  adc_ch0_val;
    reg [11:0]  adc_ch1_val;

    always @(posedge CLOCK_50 or negedge rst_n) begin
        if (!rst_n) begin
            ch_sel_reg <= 1'b0;
            adc_ch0_val <= 12'd0;
            adc_ch1_val <= 12'd0;
        end else begin
            if (w_adc_valid) begin
                if (ch_sel_reg == 1'b0)
                    adc_ch0_val <= w_adc_data;
                else
                    adc_ch1_val <= w_adc_data;
                ch_sel_reg <= ~ch_sel_reg;
            end
        end
    end

    // =========================================================
    // [신규 추가] 시스템 동작 모드 제어 (0x01: RAW, 0x02: FFT)
    // =========================================================
    wire [7:0] w_rx_cmd;
    wire       w_cmd_valid;
    reg  [7:0] system_mode; 

    always @(posedge CLOCK_50 or negedge rst_n) begin
        if (!rst_n) begin
            system_mode <= 8'h01; // 기본값은 항상 RAW 모드
        end else if (w_cmd_valid) begin
            // 0x01이나 0x02 명령어가 들어올 때만 모드 변경
            if (w_rx_cmd == 8'h01 || w_rx_cmd == 8'h02) begin
                system_mode <= w_rx_cmd;
            end
        end
    end

    // [이전 코드의 가짜 데이터 삭제]
    // reg [31:0] dummy_fft_data;
    // always @(posedge CLOCK_50...) dummy_fft_data <= dummy_fft_data + 1;

    // [신규 추가] 진짜 FFT 모듈 인스턴스 연결
    wire [31:0] real_fft_data;
    wire w_fft_done;

    fft_core_64 u_fft (
        .clk(CLOCK_50),
        .rst_n(rst_n),
        .adc_data(adc_ch0_val), // 전류 센서(CH0) 데이터만 FFT에 넣음
        .adc_valid(w_adc_valid),
        .fft_result_data(real_fft_data),
        .fft_done(w_fft_done)
    );

    // =========================================================
    // [신규 추가] 모드에 따른 전송 데이터 MUX (멀티플렉서)
    // =========================================================
    wire [15:0] ch0_word = {4'b0000, adc_ch0_val};
    wire [15:0] ch1_word = {4'b0000, adc_ch1_val};
    wire [31:0] raw_tx_data = {ch0_word, ch1_word};

    // MUX 수정: 모드 0x02일 때 가짜 데이터 대신 진짜 FFT 결과를 보냄
    wire [31:0] final_tx_data = (system_mode == 8'h02) ? real_fft_data : raw_tx_data;


    // 4) ADC 컨트롤러 인스턴스 (수정 없음)
    adc_ctrl u_adc (
        .clk(CLOCK_50),
        .rst_n(rst_n),
        .start(adc_start),
        .ch_sel(ch_sel_reg),     
        .cs_n(ADC_CS_N),
        .sclk(ADC_SCLK),
        .mosi(ADC_MOSI),
        .miso(ADC_MISO),
        .adc_data(w_adc_data),
        .valid(w_adc_valid)
    );

    // 5) Raspberry Pi용 SPI Slave 인스턴스 (포트 추가됨)
    SPI_ctrl u_rpi_spi (
        .clk(CLOCK_50),
        .rst_n(rst_n),
        .cs_n(RPI_SPI_CS_N),
        .sclk(RPI_SPI_SCLK),
        .mosi(RPI_SPI_MOSI),
        .miso(RPI_SPI_MISO),
        .tx_data(final_tx_data), // MUX를 거친 최종 데이터 연결
        .rx_cmd(w_rx_cmd),       // 수신된 커맨드 출력
        .cmd_valid(w_cmd_valid)  // 수신 완료 플래그
    );

endmodule