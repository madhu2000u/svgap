`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,write_i=0,read_i=0,valid_o;logic[7:0]data_i=0,data_o;
  fifo_empty_data dut(.*);always #5 clk=~clk;
  initial begin repeat(2)@(posedge clk);@(negedge clk);rst_n=1;write_i=1;data_i=8'h5A;
    @(posedge clk);#1;if(!valid_o||data_o!==8'h5A)$fatal(1,"fifo");
    $display("PASS");$finish;end
endmodule
