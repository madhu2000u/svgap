`timescale 1ns/1ps
module tb;
  logic[15:0]old_mstatus_i=16'h0010,write_mstatus_i=16'hA51A,write_satp_ppn_i=16'h0123;
  logic[15:0]new_mstatus_o,new_satp_ppn_o;csr_mask dut(.*);
  initial begin #1;if(new_mstatus_o!==16'hA51A||new_satp_ppn_o!==16'h0123)$fatal(1,"mask");
    $display("PASS");$finish;end
endmodule
