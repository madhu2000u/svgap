module fma_round_mode_properties;
  (* anyseq *)logic clk,rst_n,issue_i,complete_i;(* anyseq *)logic[2:0]rm_i;
  logic[2:0]rm_used_o,expected;logic pending,f_past_valid;fma_round_mode dut(.*);
  always_ff @(posedge clk) begin
    f_past_valid<=1;if(!f_past_valid)assume(!rst_n);else assume(rst_n);
    if(!rst_n)begin pending<=0;expected<=0;end
    else begin if(issue_i)begin pending<=1;expected<=rm_i;end if(complete_i&&pending)pending<=0;end
    if(f_past_valid&&$past(rst_n&&complete_i&&pending))assert(rm_used_o==$past(expected));
  end
endmodule
