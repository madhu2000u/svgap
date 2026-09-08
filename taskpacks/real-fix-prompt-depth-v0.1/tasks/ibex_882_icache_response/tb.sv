`timescale 1ns/1ps
module tb;
  logic clk=0, rst_n=0, available_i=0, ready_i=1, valid_o;
  logic [31:0] data_i=0, data_o;
  icache_response dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1;
    @(negedge clk); available_i=1; data_i=32'h12345678;
    @(posedge clk); #1; if(!valid_o || data_o!==data_i) $fatal(1,"response");
    $display("PASS"); $finish;
  end
endmodule
