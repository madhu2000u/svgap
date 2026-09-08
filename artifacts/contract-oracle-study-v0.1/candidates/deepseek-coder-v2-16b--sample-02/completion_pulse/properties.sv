module completion_pulse_properties;
  (* anyseq *) logic clk, rst_n, event_done;
  logic completed, f_past_valid;
  completion_pulse dut (.*);
  always_ff @(posedge clk) begin
    f_past_valid <= 1'b1;
    if (!f_past_valid) assume (!rst_n); else assume (rst_n);
    if (f_past_valid && $past(event_done)) assume (!event_done);
    if (f_past_valid && $past(rst_n && completed)) assert (!completed);
  end
endmodule
