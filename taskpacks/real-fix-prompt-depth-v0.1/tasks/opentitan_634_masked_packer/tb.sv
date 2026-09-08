`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,valid_i=0,ready_i=1,ready_o,valid_o;
  logic [7:0] data_i=0,data_o; logic [3:0] mask_i=0;
  masked_packer dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1;
    valid_i=1; data_i=8'hA5; mask_i=4'hF;
    @(posedge clk); #1; if(!valid_o || data_o!==8'hA5) $fatal(1,"packer");
    $display("PASS"); $finish;
  end
endmodule
