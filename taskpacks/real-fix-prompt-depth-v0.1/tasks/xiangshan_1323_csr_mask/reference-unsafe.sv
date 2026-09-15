module csr_mask(input logic[15:0]old_mstatus_i,write_mstatus_i,
  input logic[15:0]write_satp_ppn_i,output logic[15:0]new_mstatus_o,new_satp_ppn_o);
  assign new_mstatus_o=write_mstatus_i;assign new_satp_ppn_o=write_satp_ppn_i;
endmodule
