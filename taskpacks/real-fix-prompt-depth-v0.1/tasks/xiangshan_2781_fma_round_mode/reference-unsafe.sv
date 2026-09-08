module fma_round_mode(input logic clk,rst_n,issue_i,
  input logic[2:0]rm_i,input logic complete_i,output logic[2:0]rm_used_o);
  always_ff @(posedge clk) begin
    if(!rst_n)rm_used_o<=0;else if(complete_i)rm_used_o<=rm_i;
  end
endmodule
