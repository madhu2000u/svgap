module ahb_error_completion(input logic clk,rst_n,
  input logic transfer_i,done_i,error_i,output logic dv_o);
  always_ff @(posedge clk) begin
    if(!rst_n) dv_o<=0;
    else if(dv_o && (done_i||error_i)) dv_o<=0;
    else if(transfer_i) dv_o<=1;
  end
endmodule
