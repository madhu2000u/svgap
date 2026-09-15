module stream_hold(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       s_valid,
    input  logic [7:0] s_data,
    output logic       s_ready,
    output logic       m_valid,
    output logic [7:0] m_data,
    input  logic       m_ready
);
    logic valid_reg;
    logic [7:0] data_reg;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid_reg <= 1'b0;
            data_reg <= 8'd0;
        end else begin
            if (s_valid && s_ready) begin
                valid_reg <= m_ready;
                data_reg <= s_data;
            end
        end
    end

    assign s_ready = !valid_reg || m_ready;
    assign m_valid = valid_reg;
    assign m_data = data_reg;

endmodule
