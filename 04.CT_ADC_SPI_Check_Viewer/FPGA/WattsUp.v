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

    // 테스트 중에는 버튼 하나를 리셋으로 쓰는 게 안전함
    wire rst_n = KEY[0];

    // -------------------------------------------------
    // 1) ADC 측정 주기 생성
    // -------------------------------------------------
    reg [15:0] timer_cnt;
    reg adc_start;

    always @(posedge CLOCK_50 or negedge rst_n) begin
        if (!rst_n) begin
            timer_cnt  <= 16'd0;
            adc_start  <= 1'b0;
        end else begin
            if (timer_cnt == 16'd50000) begin
                timer_cnt <= 16'd0;
                adc_start <= 1'b1;   // 1ms마다 start pulse
            end else begin
                timer_cnt <= timer_cnt + 16'd1;
                adc_start <= 1'b0;
            end
        end
    end

    // -------------------------------------------------
    // 2) ADC 읽기 관련 내부 신호
    // -------------------------------------------------
    wire [11:0] w_adc_data;
    wire        w_adc_valid;

    reg         ch_sel_reg;      // 0: CH0, 1: CH1
    reg [11:0]  adc_ch0_val;
    reg [11:0]  adc_ch1_val;

    // valid가 뜰 때 현재 채널 값을 저장하고 다음 채널로 전환
    always @(posedge CLOCK_50 or negedge rst_n) begin
        if (!rst_n) begin
            ch_sel_reg <= 1'b0;      // 처음엔 CH0부터
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

    // -------------------------------------------------
    // 3) Raspberry Pi로 보낼 32비트 데이터 구성
    //    [31:16] = CH0
    //    [15: 0] = CH1
    // -------------------------------------------------
    wire [15:0] ch0_word;
    wire [15:0] ch1_word;
    wire [31:0] tx_data_32;

    assign ch0_word  = {4'b0000, adc_ch0_val};
    assign ch1_word  = {4'b0000, adc_ch1_val};
    assign tx_data_32 = {ch0_word, ch1_word};

    // -------------------------------------------------
    // 4) ADC 컨트롤러 인스턴스
    // -------------------------------------------------
    adc_ctrl u_adc (
        .clk(CLOCK_50),
        .rst_n(rst_n),
        .start(adc_start),
        .ch_sel(ch_sel_reg),     // CH0/CH1 번갈아 읽기
        .cs_n(ADC_CS_N),
        .sclk(ADC_SCLK),
        .mosi(ADC_MOSI),
        .miso(ADC_MISO),
        .adc_data(w_adc_data),
        .valid(w_adc_valid)
    );

    // -------------------------------------------------
    // 5) Raspberry Pi용 SPI Slave 인스턴스
    // -------------------------------------------------
    SPI_Slave u_rpi_spi (
        .clk(CLOCK_50),
        .rst_n(rst_n),
        .cs_n(RPI_SPI_CS_N),
        .sclk(RPI_SPI_SCLK),
        .mosi(RPI_SPI_MOSI),
        .miso(RPI_SPI_MISO),
        .tx_data(tx_data_32)
    );

endmodule