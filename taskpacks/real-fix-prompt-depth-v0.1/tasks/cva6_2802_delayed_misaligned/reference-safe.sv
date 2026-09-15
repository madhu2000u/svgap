module delayed_misaligned(input logic clk,rst_n,request_i,
  input logic misaligned_i,output logic response_o,misaligned_o);
  always_ff @(posedge clk) begin
    if(!rst_n) begin response_o<=0;misaligned_o<=0;end
    else begin response_o<=request_i;misaligned_o<=request_i&&misaligned_i;end
  end
endmodule
