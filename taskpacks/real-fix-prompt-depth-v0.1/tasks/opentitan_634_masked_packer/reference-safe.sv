module masked_packer(input logic clk,rst_n,valid_i,
  input logic [7:0] data_i,input logic [3:0] mask_i,output logic ready_o,
  output logic valid_o,output logic [7:0] data_o,input logic ready_i);
  assign ready_o=!valid_o||ready_i;
  always_ff @(posedge clk) begin
    if(!rst_n) begin valid_o<=0; data_o<=0; end
    else if(ready_o) begin valid_o<=valid_i&&(mask_i==4'hF); if(valid_i) data_o<=data_i; end
  end
endmodule
