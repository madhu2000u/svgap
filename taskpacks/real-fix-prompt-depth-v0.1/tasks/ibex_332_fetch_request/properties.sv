module fetch_request_properties;
  (* anyseq *) logic clk,rst_n,start_i,redirect_i,gnt_i;
  (* anyseq *) logic [31:0] start_addr_i,redirect_addr_i;
  logic req_o,f_past_valid; logic [31:0] addr_o;
  fetch_request dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n && req_o && !gnt_i)) begin
      assert(req_o); assert(addr_o==$past(addr_o));
    end
  end
endmodule
