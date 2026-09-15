module masked_packer_properties;
  (* anyseq *) logic clk,rst_n,valid_i,ready_i; (* anyseq *) logic [7:0] data_i;
  (* anyseq *) logic [3:0] mask_i; logic ready_o,valid_o,f_past_valid;
  logic [7:0] data_o; masked_packer dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n&&valid_o&&!ready_i)) begin
      assert(valid_o); assert(data_o==$past(data_o));
    end
    if(valid_o&&!ready_i) assert(!ready_o);
  end
endmodule
