module irq_pulse(input logic clk, input logic rst_n,
  input logic trigger, output logic irq);
  logic hold;
  always_ff @(posedge clk) begin
    if (!rst_n) begin irq <= 0; hold <= 0; end
    else begin hold <= trigger; irq <= trigger || hold; end
  end
endmodule
