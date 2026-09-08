module csr_mask(input logic[15:0]old_mstatus_i,write_mstatus_i,
  input logic[15:0]write_satp_ppn_i,output logic[15:0]new_mstatus_o,new_satp_ppn_o);
  always_comb begin
    new_mstatus_o=(write_mstatus_i&16'hFFCF)|(old_mstatus_i&16'h0030);
    new_satp_ppn_o={4'b0,write_satp_ppn_i[11:0]};
  end
endmodule
