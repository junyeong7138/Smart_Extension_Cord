module SPI_Slave(
    input clk,
    input rst_n,

    input cs_n,
    input sclk,
    input mosi,
    output reg miso,

    input [31:0] tx_data
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

    wire sclk_fall  = (sclk_sync[2:1] == 2'b10);
    wire cs_n_fall  = (cs_n_sync[2:1] == 2'b10);
    wire cs_active  = ~cs_n_sync[1];

    reg [31:0] shift_reg_tx;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            miso <= 1'b0;
            shift_reg_tx <= 32'h00000000;
        end else begin
            if (!cs_active) begin
                // CS 비활성 상태
                miso <= 1'b0;
            end else begin
                // CS가 내려가는 순간: 전송 데이터 장전
                if (cs_n_fall) begin
                    shift_reg_tx <= tx_data;
                    miso <= tx_data[31];
                end
                // SCLK falling edge마다 다음 비트 출력
                else if (sclk_fall) begin
                    shift_reg_tx <= {shift_reg_tx[30:0], 1'b0};
                    miso <= shift_reg_tx[30];
                end
            end
        end
    end

endmodule