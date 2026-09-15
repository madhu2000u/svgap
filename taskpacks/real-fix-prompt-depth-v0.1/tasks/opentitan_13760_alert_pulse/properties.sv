module alert_pulse_properties;
  (* anyseq *)logic clk,rst_n,bad_field_i;logic alert_o,f_past_valid;alert_pulse dut(.*);
  always_ff @(posedge clk)begin
    f_past_valid<=1;if(!f_past_valid)assume(!rst_n);else assume(rst_n);
    if(f_past_valid&&$past(rst_n&&alert_o&&bad_field_i))begin assume(bad_field_i);assert(!alert_o);end
  end
endmodule
