module icache_response_properties;
  (* anyseq *) logic clk, rst_n, available_i, ready_i;
  (* anyseq *) logic [31:0] data_i;
  logic valid_o, f_past_valid; logic [31:0] data_o;
  icache_response dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if (!f_past_valid) assume(!rst_n); else assume(rst_n);
    if (f_past_valid && $past(rst_n && available_i && !ready_i)) assert(valid_o);
    if (f_past_valid && $past(rst_n && valid_o && !ready_i)) begin
      assert(valid_o); assert(data_o==$past(data_o));
    end
  end
endmodule
