module split_store_properties;
  (* anyseq *) logic clk,rst_n,start_i,first_done_i,first_error_i,second_done_i;
  logic second_req_o,complete_o,fault_o,f_past_valid;
  split_store dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid&&rst_n&&fault_o) assert($past(second_done_i));
  end
endmodule
