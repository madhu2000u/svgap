module ahb_error_completion(input logic clk,rst_n,
  input logic transfer_i,done_i,error_i,output logic dv_o);
  logic retire_q;
  always_ff @(posedge clk) begin
    if(!rst_n) begin dv_o<=0; retire_q<=0; end
    else begin
      retire_q<=dv_o&&(done_i||error_i);
      if(retire_q) dv_o<=0; else if(transfer_i) dv_o<=1;
    end
  end
endmodule
