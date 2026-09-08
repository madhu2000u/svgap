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

logic [15:0] storage;
logic valid_reg;

always_ff @(posedge clk or negedge rst_n) begin : proc_result_hold
    if (!rst_n) begin
        produce_ready <= 1'b1; // Ready to accept production when reset is active
        result_valid  <= 1'b0;
        storage       <= 16'd0;
        valid_reg     <= 1'b0;
    end else if (produce && produce_ready) begin
        // Accept new result and update validity
        storage   <= result_in;
        result_valid <= 1'b1;
        valid_reg   <= 1'b1;
        produce_ready <= 1'b0; // Once produced, not ready for next until accepted
    end else if (result_valid && !result_ready) begin
        // Hold the current result while waiting for acceptance
        result_valid <= 1'b1;
        valid_reg   <= 1'b1;
    end else if (!result_valid || result_ready) begin
        // Reset validity and prepare to accept new data or when ready is asserted
        result_valid <= 1'b0;
        valid_reg   <= 1'b0;
        produce_ready <= 1'b1; // Ready for next production cycle after acceptance
    end
end

assign result_out = storage;

endmodule
