module SPI_Slave(
    input clk,            // DE2-115 보드의 50MHz 메인 클럭
    input rst_n,          // 리셋 (Active Low)
    
    // 라즈베리파이(Master)와 연결될 SPI 핀들
    input cs_n,           // 칩 선택 신호 (RPi가 0으로 내리면 통신 시작)
    input sclk,           // SPI 클럭 (RPi가 제공)
    input mosi,           // RPi -> FPGA (지금 당장은 안 쓰지만 구조상 입력으로 둠)
    output reg miso,      // FPGA -> RPi (버튼 데이터를 RPi로 전송!)
    
    input [7:0] tx_data   // 버튼이 눌렸을 때 보낼 데이터
);

    // 라즈베리파이의 클럭(sclk)과 칩 선택(cs_n) 신호를 50MHz에 동기화
    // (비동기 신호로 인한 메타스테빌리티 방지용 3단 플립플롭)
    reg [2:0] sclk_sync;
    reg [2:0] cs_n_sync;
    always @(posedge clk) begin
        sclk_sync <= {sclk_sync[1:0], sclk};
        cs_n_sync <= {cs_n_sync[1:0], cs_n};
    end

    // 엣지(에지) 검출: 클럭이 올라가고 내려가는 순간을 포착
    wire sclk_rise = (sclk_sync[2:1] == 2'b01);
    wire sclk_fall = (sclk_sync[2:1] == 2'b10);
    wire cs_n_active = ~cs_n_sync[1];             // cs_n이 0일 때 Active
    wire cs_n_fall = (cs_n_sync[2:1] == 2'b10);   // 통신 시작 순간

    reg [7:0] shift_reg_tx;

    // SPI Mode 0 (CPOL=0, CPHA=0) 슬레이브 송신 로직
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            miso <= 1'bZ;  // 통신 안 할 때는 끊어둠 (High Impedance)
            shift_reg_tx <= 8'h00;
        end else begin
            if (!cs_n_active) begin
                miso <= 1'bZ; // CS가 1이면 선을 놓아줌
            end else begin
                // 통신이 막 시작된 순간 (CS_N 하강 에지)
                if (cs_n_fall) begin
                    shift_reg_tx <= tx_data;     // 보낼 데이터 장전
                    miso <= tx_data[7];          // 첫 번째 비트(MSB)를 미리 MISO 선에 올림
                end 
                // 통신 중 (SCLK 하강 에지마다 다음 비트로 넘어감)
                else if (sclk_fall) begin
                    shift_reg_tx <= {shift_reg_tx[6:0], 1'b0};
                    miso <= shift_reg_tx[6];     // 다음 비트를 MISO 선에 올림
                end
            end
        end
    end
endmodule
