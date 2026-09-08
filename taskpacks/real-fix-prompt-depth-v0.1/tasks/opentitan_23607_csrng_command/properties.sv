module csrng_command_properties;
  (* anyseq *) logic clk,rst_n,submit_i,cmd_ready_i,status_error_i;
  (* anyseq *) logic [7:0] submit_cmd_i; logic cmd_valid_o,error_seen_o,f_past_valid;
  logic [7:0] cmd_o; csrng_command dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;
    if(!f_past_valid) assume(!rst_n); else assume(rst_n);
    if(f_past_valid && $past(rst_n&&cmd_valid_o&&!cmd_ready_i)) begin
      assert(cmd_valid_o); assert(cmd_o==$past(cmd_o));
    end
  end
endmodule
