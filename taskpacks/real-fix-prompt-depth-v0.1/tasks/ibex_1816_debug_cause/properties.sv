module debug_cause_properties;
  (* anyseq *) logic clk,rst_n,enter_debug_i,debug_req_i,save_cause_i;
  logic cause_haltreq_o,f_past_valid,pending,expected;
  debug_cause dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(!rst_n) begin pending<=0;expected<=0;end
    else begin
      if(enter_debug_i) begin pending<=1;expected<=debug_req_i;end
      if(save_cause_i&&pending) pending<=0;
    end
    if(f_past_valid && $past(rst_n&&save_cause_i&&pending))
      assert(cause_haltreq_o==$past(expected));
  end
endmodule
