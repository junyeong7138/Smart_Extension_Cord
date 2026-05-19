module SPI_ctrl(
    input clk,
    input rst_n,

    input cs_n,
    input sclk,
    input mosi,
    output reg miso,

    input [31:0] tx_data,
    
    // 새로 추가된 출력: 라즈베리파이로부터 받은 8비트 명령어
    output reg [7:0] rx_cmd,   
    output reg cmd_valid       
);

    // 비동기 입력 동기화
    reg [2:0] sclk_sync;
    reg [2:0] cs_n_sync;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sclk_sync <= 3'b000;
            cs_n_sync <= 3'b111;
        end else begin
            sclk_sync <= {sclk_sync[1:0], sclk};
            cs_n_sync <= {cs_n_sync[1:0], cs_n};
        end
    end

    wire sclk_rise  = (sclk_sync[2:1] == 2'b01); // MOSI 데이터를 읽기 위한 Rising Edge 감지
    wire sclk_fall  = (sclk_sync[2:1] == 2'b10);
    wire cs_n_fall  = (cs_n_sync[2:1] == 2'b10);
    wire cs_n_rise  = (cs_n_sync[2:1] == 2'b01); // 통신 종료 감지
    wire cs_active  = ~cs_n_sync[1];

    reg [31:0] shift_reg_tx;
    reg [31:0] shift_reg_rx; // 32비트 수신 버퍼 추가

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            miso <= 1'b0;
            shift_reg_tx <= 32'h00000000;
            shift_reg_rx <= 32'h00000000;
            rx_cmd <= 8'h00;
            cmd_valid <= 1'b0;
        end else begin
            cmd_valid <= 1'b0; // 기본적으로 0, 수신 완료 시 1클럭 동안만 High
            
            if (!cs_active) begin
                miso <= 1'b0;
                // CS가 High로 올라가면(통신 1사이클 종료), 수신된 32비트 중 첫 8비트를 커맨드로 인식
                if (cs_n_rise) begin
                    rx_cmd <= shift_reg_rx[31:24]; 
                    cmd_valid <= 1'b1;
                end
            end else begin
                // CS가 내려가는 순간: 송신 데이터 장전
                if (cs_n_fall) begin
                    shift_reg_tx <= tx_data;
                    miso <= tx_data[31];
                end
                // SCLK falling edge마다 다음 비트 출력 (MISO)
                else if (sclk_fall) begin
                    shift_reg_tx <= {shift_reg_tx[30:0], 1'b0};
                    miso <= shift_reg_tx[30];
                end
                
                // SCLK rising edge마다 마스터의 데이터 읽기 (MOSI)
                if (sclk_rise) begin
                    shift_reg_rx <= {shift_reg_rx[30:0], mosi};
                end
            end
        end
    end
endmodule