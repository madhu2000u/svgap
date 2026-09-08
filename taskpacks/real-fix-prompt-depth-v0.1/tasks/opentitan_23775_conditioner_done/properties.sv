module conditioner_done_properties;
  (* anyseq *)logic clk,rst_n,word_valid_i,word_ready_i,window_last_i;
  logic process_o,f_past_valid;conditioner_done dut(.*);
  always_ff @(posedge clk)begin
    f_past_valid<=1;if(!f_past_valid)assume(!rst_n);else assume(rst_n);
    if(f_past_valid&&$past(rst_n))
      assert(process_o==$past(word_valid_i&&word_ready_i&&window_last_i));
  end
endmodule
