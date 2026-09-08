module result_hold(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        produce,
    input  logic [15:0] result_in,
    output logic        produce_ready,
    output logic        result_valid,
    output logic [15:0] result_out,
    input  logic        result_ready
);
    logic        valid_reg;
    logic [15:0] data_reg;

    assign produce_ready = !valid_reg || result_ready;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            valid_reg <= 0;
            data_reg <= 0;
        end else begin
            if (produce && produce_ready) begin
                valid_reg <= 1;
                data_reg <= result_in;
            end else if (result_valid && !result_ready) begin
                // Hold the value stable
            end else if (result_valid && result_ready) begin
                valid_reg <= 0;
            end
        end
    end

    assign result_valid = valid_reg;
    assign result_out = data_reg;
endmodule
