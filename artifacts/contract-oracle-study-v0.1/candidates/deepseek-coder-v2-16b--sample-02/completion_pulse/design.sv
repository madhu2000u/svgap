module completion_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic event_done,
    output logic completed
);

    // Internal signal to store the state of the completion pulse
    logic completion_reg;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Asynchronous reset: clear the completion pulse
            completion_reg <= 1'b0;
        end else begin
            // On each clock cycle, set the completion pulse if event_done is high
            if (event_done) begin
                completion_reg <= 1'b1;
            end else begin
                // Ensure that completed remains low on subsequent cycles even if no other events occur
                completion_reg <= 1'b0;
            end
        end
    end

    assign completed = completion_reg;

endmodule
