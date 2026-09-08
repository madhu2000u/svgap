`timescale 1ns/1ps
module tb;
  logic illegal_i=1,virt_i=1,valid_o,gva_o;logic[31:0]instr_i=32'hDEADBEEF;
  logic[5:0]cause_o;logic[31:0]tval_o,htval_o,mtinst_o;exception_record dut(.*);
  initial begin #1;if(!valid_o||cause_o!==6'd2||tval_o!==instr_i)$fatal(1,"exception");
    $display("PASS");$finish;end
endmodule
