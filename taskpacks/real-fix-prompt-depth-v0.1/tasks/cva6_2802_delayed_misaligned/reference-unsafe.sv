module delayed_misaligned(input logic clk,rst_n,request_i,
  input logic misaligned_i,output logic response_o,misaligned_o);
  always_ff @(posedge clk) begin if(!rst_n) response_o<=0;else response_o<=request_i;end
  assign misaligned_o=response_o&&misaligned_i;
endmodule
