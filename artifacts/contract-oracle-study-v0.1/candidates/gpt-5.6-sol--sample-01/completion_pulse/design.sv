module completion_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic event_done,
    output logic completed
);

    always_ff @(posedge clk) begin
        if (!rst_n)
            completed <= 1'b0;
        else
            completed <= event_done;
    end

endmodule
