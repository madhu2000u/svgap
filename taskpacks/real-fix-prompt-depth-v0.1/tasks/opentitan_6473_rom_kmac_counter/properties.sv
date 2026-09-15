module rom_kmac_counter_properties;
  (* anyseq *) logic clk,rst_n,word_valid_i,kmac_ready_i;
  logic f_past_valid; logic [7:0] addr_o; rom_kmac_counter dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n)) begin
      if($past(word_valid_i&&kmac_ready_i)) assert(addr_o==$past(addr_o)+1'b1);
      else assert(addr_o==$past(addr_o));
    end
  end
endmodule
