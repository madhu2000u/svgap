module ahb_error_completion_properties;
  (* anyseq *) logic clk,rst_n,transfer_i,done_i,error_i;
  logic dv_o,f_past_valid; ahb_error_completion dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n && dv_o && (done_i||error_i))) assert(!dv_o);
  end
endmodule
