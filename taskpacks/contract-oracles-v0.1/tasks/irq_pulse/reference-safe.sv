module irq_pulse(input logic clk, input logic rst_n,
  input logic trigger, output logic irq);
  always_ff @(posedge clk) begin if (!rst_n) irq <= 0; else irq <= trigger; end
endmodule
