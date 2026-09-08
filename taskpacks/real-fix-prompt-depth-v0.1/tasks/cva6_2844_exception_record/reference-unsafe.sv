module exception_record(input logic illegal_i,virt_i,
  input logic[31:0]instr_i,output logic valid_o,output logic[5:0]cause_o,
  output logic[31:0]tval_o,htval_o,mtinst_o,output logic gva_o);
  always_comb begin
    valid_o=illegal_i;cause_o=illegal_i?6'd2:0;tval_o=illegal_i?instr_i:0;gva_o=virt_i;
    htval_o=illegal_i?instr_i:0;mtinst_o=illegal_i?instr_i:0;
  end
endmodule
