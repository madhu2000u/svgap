module irq_pulse_properties;
  (* anyseq *) logic clk, rst_n, trigger;
  logic irq, f_past_valid;
  irq_pulse dut (.*);
  always_ff @(posedge clk) begin
    f_past_valid <= 1'b1;
    if (!f_past_valid) assume (!rst_n); else assume (rst_n);
    if (f_past_valid && $past(trigger)) assume (!trigger);
    if (f_past_valid && $past(rst_n && irq)) assert (!irq);
  end
endmodule
