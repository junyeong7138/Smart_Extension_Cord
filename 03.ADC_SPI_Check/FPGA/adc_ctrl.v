module adc_ctrl(
    input clk,
    input rst_n,
    input start,
    input ch_sel,         // 0: CH0, 1: CH1

    output reg cs_n,
    output reg sclk,
    output reg mosi,
    input miso,

    output reg [11:0] adc_data,
    output reg valid
);

    reg [8:0] clk_cnt;
    reg [4:0] bit_cnt;
    reg [2:0] cmd;
    reg [11:0] rx_temp;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cs_n <= 1'b1;
            sclk <= 1'b0;
            mosi <= 1'b0;
            valid <= 1'b0;
            bit_cnt <= 5'd0;
            clk_cnt <= 9'd0;
            adc_data <= 12'd0;
            rx_temp <= 12'd0;
        end else begin
            if (cs_n == 1'b1) begin
                valid <= 1'b0;

                if (start) begin
                    cs_n <= 1'b0;
                    cmd <= {1'b1, ch_sel, 1'b1}; // SGL=1, CH=ch_sel, MSBF=1
                    mosi <= 1'b1;                // Start bit
                    bit_cnt <= 5'd0;
                    clk_cnt <= 9'd0;
                    sclk <= 1'b0;
                    rx_temp <= 12'd0;
                end
            end else begin
                clk_cnt <= clk_cnt + 9'd1;

                // rising edge: MISO 샘플링
                if (clk_cnt == 9'd249) begin
                    sclk <= 1'b1;
                    if (bit_cnt >= 5 && bit_cnt <= 16) begin
                        rx_temp <= {rx_temp[10:0], miso};
                    end
                end
                // falling edge: MOSI 출력
                else if (clk_cnt == 9'd499) begin
                    sclk <= 1'b0;
                    clk_cnt <= 9'd0;

                    if (bit_cnt < 3)
                        mosi <= cmd[2 - bit_cnt];
                    else
                        mosi <= 1'b0;

                    bit_cnt <= bit_cnt + 5'd1;

                    if (bit_cnt == 16) begin
                        cs_n <= 1'b1;
                        valid <= 1'b1;
                        adc_data <= rx_temp;
                    end
                end
            end
        end
    end
endmodule