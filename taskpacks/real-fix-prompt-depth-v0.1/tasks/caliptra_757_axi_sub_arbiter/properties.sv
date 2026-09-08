module axi_sub_arbiter_properties;
  (* anyseq *) logic clk,rst_n,read_valid_i,write_valid_i,out_ready_i;
  (* anyseq *) logic [15:0] read_addr_i,write_addr_i;
  logic out_valid_o,out_is_write_o,f_past_valid; logic [15:0] out_addr_o;
  axi_sub_arbiter dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n && out_valid_o && !out_ready_i)) begin
      assert(out_valid_o); assert(out_is_write_o==$past(out_is_write_o));
      assert(out_addr_o==$past(out_addr_o));
    end
  end
endmodule
