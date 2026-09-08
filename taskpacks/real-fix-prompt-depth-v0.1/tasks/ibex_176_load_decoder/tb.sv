`timescale 1ns/1ps
module tb;logic[6:0]opcode_i=7'b0000011;logic[2:0]funct3_i=3'b010;
  logic valid_load_o,illegal_o;load_decoder dut(.*);
  initial begin #1;if(!valid_load_o||illegal_o)$fatal(1,"lw");$display("PASS");$finish;end
endmodule
