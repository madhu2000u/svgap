`timescale 1ns/1ps
module tb;
  logic enable_i=1;logic[1:0]slot_valid_i=2'b01;logic valid_o;iti_valid dut(.*);
  initial begin #1;if(!valid_o)$fatal(1,"valid");$display("PASS");$finish;end
endmodule
