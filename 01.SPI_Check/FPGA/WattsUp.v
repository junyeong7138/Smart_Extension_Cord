module WattsUp(
    input CLOCK_50,       // 50MHz 시스템 클럭
    input [3:0] KEY,      // DE2-115 버튼
    output [3:0] LEDG,    // 초록색 LED
    
    // SPI Pin (라즈베리파이=Master, FPGA=Slave)
    input SPI_SCLK,       // 입력으로 변경됨! (RPi가 생성)
    input SPI_CS_N,       // 입력으로 변경됨! (RPi가 생성)
    input SPI_MOSI,       // 입력으로 변경됨! (RPi가 생성)
    output SPI_MISO       // 새롭게 추가됨! (FPGA가 RPi로 데이터 쏨)
);

    wire rst_n = 1'b1;
    reg [3:0] led_reg = 4'b0000;
    assign LEDG = led_reg;

    // --- 디바운싱 로직 ---
    reg [19:0] count;
    reg [3:0] key_db;
    always @(posedge CLOCK_50) begin
        count <= count + 1;
        if (count == 0) key_db <= ~KEY; 
    end

    reg [3:0] key_db_delay;
    wire [3:0] btn_edge = key_db & ~key_db_delay; 
    always @(posedge CLOCK_50) key_db_delay <= key_db;

    // --- 버튼 데이터 저장 로직 ---
    reg [7:0] spi_tx_data = 8'h00; // 라즈베리파이로 보낼 값을 들고 있는 레지스터

    always @(posedge CLOCK_50) begin
        if (btn_edge[0]) begin
            led_reg[0] <= ~led_reg[0];
            spi_tx_data <= 8'hA1; 
        end else if (btn_edge[1]) begin
            led_reg[1] <= ~led_reg[1];
            spi_tx_data <= 8'hB2; 
        end else if (btn_edge[2]) begin
            led_reg[2] <= ~led_reg[2];
            spi_tx_data <= 8'hC3; 
        end else if (btn_edge[3]) begin
            led_reg[3] <= ~led_reg[3];
            spi_tx_data <= 8'hD4; 
        end
    end

    // --- SPI Slave 모듈 연결 ---
    SPI_Slave u0 (
        .clk(CLOCK_50),
        .rst_n(rst_n),
        .cs_n(SPI_CS_N),
        .sclk(SPI_SCLK),
        .mosi(SPI_MOSI),
        .miso(SPI_MISO),      // 새로 생긴 MISO 선 연결
        .tx_data(spi_tx_data)
    );

endmodule
