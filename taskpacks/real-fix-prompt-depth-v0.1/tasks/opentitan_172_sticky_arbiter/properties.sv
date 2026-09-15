module sticky_arbiter_properties;
  (* anyseq *) logic clk,rst_n,ack_i; (* anyseq *) logic [2:0] req_i;
  (* anyseq *) logic [23:0] data_i; logic valid_o,f_past_valid;
  logic [2:0] grant_o; logic [7:0] data_o; sticky_arbiter dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n&&valid_o&&!ack_i)) begin
      assert(valid_o); assert(grant_o==$past(grant_o)); assert(data_o==$past(data_o));
    end
    if(valid_o) assert(grant_o==3'b001||grant_o==3'b010||grant_o==3'b100);
  end
endmodule
