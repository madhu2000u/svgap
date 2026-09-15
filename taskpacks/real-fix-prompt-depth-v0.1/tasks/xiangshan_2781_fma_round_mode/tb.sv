`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,issue_i=0,complete_i=0;logic[2:0]rm_i=0,rm_used_o;
  fma_round_mode dut(.*);always #5 clk=~clk;
  initial begin
    repeat(2)@(posedge clk);@(negedge clk);rst_n=1;issue_i=1;rm_i=3'd3;
    @(negedge clk);issue_i=0;complete_i=1;
    @(posedge clk);#1;if(rm_used_o!==3'd3)$fatal(1,"rm");
    $display("PASS");$finish;
  end
endmodule
