module wakeup_latch_properties;
  (* anyseq *)logic clk,rst_n,sleeping_i,wakeup_event_i,clear_cause_i;
  logic wakeup_o,f_past_valid;wakeup_latch dut(.*);
  always_ff @(posedge clk)begin
    f_past_valid<=1;if(!f_past_valid)assume(!rst_n);else assume(rst_n);
    if(f_past_valid&&$past(rst_n&&wakeup_o&&!clear_cause_i))assert(wakeup_o);
  end
endmodule
