`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,ack_i=1,valid_o; logic [2:0] req_i=0,grant_o;
  logic [23:0] data_i=24'h332211; logic [7:0] data_o;
  sticky_arbiter dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1; req_i=3'b010;
    @(posedge clk); #1; if(!valid_o || grant_o!==3'b010 || data_o!==8'h22) $fatal(1,"arb");
    $display("PASS"); $finish;
  end
endmodule
