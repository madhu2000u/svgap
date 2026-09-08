module delayed_misaligned_properties;
  (* anyseq *) logic clk,rst_n,request_i,misaligned_i;
  logic response_o,misaligned_o,f_past_valid; delayed_misaligned dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid&&$past(rst_n)) begin
      assert(response_o==$past(request_i));
      assert(misaligned_o==($past(request_i)&&$past(misaligned_i)));
    end
  end
endmodule
