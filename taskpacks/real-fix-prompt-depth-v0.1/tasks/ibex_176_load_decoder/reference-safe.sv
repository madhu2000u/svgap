module load_decoder(input logic[6:0]opcode_i,input logic[2:0]funct3_i,
  output logic valid_load_o,illegal_o);logic supported;
  always_comb begin
    supported=(funct3_i==0)||(funct3_i==1)||(funct3_i==2)||(funct3_i==4)||(funct3_i==5);
    valid_load_o=(opcode_i==7'b0000011)&&supported;
    illegal_o=(opcode_i==7'b0000011)&&!supported;
  end
endmodule
