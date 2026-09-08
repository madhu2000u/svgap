`timescale 1ns/1ps
module tb;
  logic[7:0]addr_i=8'h10,lo0_i=8'h00,hi0_i=8'h1F,lo1_i=8'h80,hi1_i=8'h8F;
  logic read_i=1,en0_i=1,allow_r0_i=1,allow_w0_i=0,en1_i=1,allow_r1_i=0,allow_w1_i=1;
  logic matched_o,allow_o,index_o;range_priority dut(.*);
  initial begin #1;if(!matched_o||!allow_o||index_o)$fatal(1,"range");$display("PASS");$finish;end
endmodule
