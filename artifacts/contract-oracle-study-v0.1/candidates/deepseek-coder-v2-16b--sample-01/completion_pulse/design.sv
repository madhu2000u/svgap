module completion_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic event_done,
    output logic completed
);

    // State variable to track if an event has been processed
    logic event_processed;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Asynchronous reset: clear the state and output
            event_processed <= 1'b0;
            completed <= 1'b0;
        end else begin
            // On each clock cycle, check if an event has occurred
            if (event_done) begin
                // Set the flag to indicate that an event has been processed
                event_processed <= 1'b1;
            end

            // Generate the completed pulse for one cycle
            completed <= event_processed;

            // Clear the event_processed flag after it has been used
            if (event_done || !rst_n) begin
                event_processed <= 1'b0;
            end
        end
    end
endmodule
