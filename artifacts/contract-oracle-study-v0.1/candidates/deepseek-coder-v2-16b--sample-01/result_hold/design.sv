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

always_ff @(posedge clk or negedge rst_n) begin : proc_result_hold
    if (!rst_n) begin
        produce_ready <= 1'b1; // Ready to accept production when reset is active
        result_valid  <= 1'b0;
        storage       <= 16'h0;
    end else begin
        if (produce && produce_ready) begin
            storage   <= result_in; // Accept new result when produce and ready are asserted
            produce_ready <= 1'b0; // Once accepted, indicate not ready for next production
            result_valid  <= 1'b1; // Result is now valid
        end else if (result_valid && !result_ready) begin
            // Hold the current result while it is not ready to be consumed
            result_valid  <= 1'b1;
            result_out    <= storage; // Keep the stored value stable until accepted
        end else if (result_ready) begin
            // If result is ready, reset valid and prepare for next production
            produce_ready <= 1'b1;
            result_valid  <= 1'b0;
        end
    end
end

endmodule
