module irq_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic trigger,
    output logic irq
);
    logic irq_reg;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            irq_reg <= 0;
        end else begin
            irq_reg <= trigger & ~irq_reg;
        end
    end

    assign irq = irq_reg;

endmodule
