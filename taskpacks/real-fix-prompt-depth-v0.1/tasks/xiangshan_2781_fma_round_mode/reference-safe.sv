module fma_round_mode(input logic clk,rst_n,issue_i,
  input logic[2:0]rm_i,input logic complete_i,output logic[2:0]rm_used_o);
  logic[2:0]rm_q;
  always_ff @(posedge clk) begin
    if(!rst_n)begin rm_q<=0;rm_used_o<=0;end
    else begin if(issue_i)rm_q<=rm_i;if(complete_i)rm_used_o<=rm_q;end
  end
endmodule
