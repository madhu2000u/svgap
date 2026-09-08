module exception_record(input logic illegal_i,virt_i,
  input logic[31:0]instr_i,output logic valid_o,output logic[5:0]cause_o,
  output logic[31:0]tval_o,htval_o,mtinst_o,output logic gva_o);
  always_comb begin
    valid_o=0;cause_o=0;tval_o=0;htval_o=0;mtinst_o=0;gva_o=0;
    if(illegal_i)begin valid_o=1;cause_o=6'd2;tval_o=instr_i;gva_o=virt_i;end
  end
endmodule
