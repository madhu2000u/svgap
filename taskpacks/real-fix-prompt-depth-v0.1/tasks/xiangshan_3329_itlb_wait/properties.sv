module itlb_wait_properties;
  (* anyseq *)logic clk,rst_n,request_i,tlb_valid_i;logic pending_o,done_o,f_past_valid;
  itlb_wait dut(.*);
  always_ff @(posedge clk)begin
    f_past_valid<=1;if(!f_past_valid)assume(!rst_n);else assume(rst_n);
    if(pending_o&&!tlb_valid_i)assert(!done_o);
    if(f_past_valid&&$past(rst_n&&pending_o&&!tlb_valid_i))assert(pending_o&&!done_o);
  end
endmodule
