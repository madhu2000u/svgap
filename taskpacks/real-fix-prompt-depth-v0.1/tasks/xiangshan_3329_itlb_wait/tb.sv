`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,request_i=0,tlb_valid_i=0,pending_o,done_o;
  itlb_wait dut(.*);always #5 clk=~clk;
  initial begin
    repeat(2)@(posedge clk);@(negedge clk);rst_n=1;request_i=1;tlb_valid_i=1;
    @(posedge clk);#1;if(!pending_o)$fatal(1,"pending");
    @(negedge clk);request_i=0;
    @(posedge clk);#1;if(!done_o)$fatal(1,"done");
    $display("PASS");$finish;
  end
endmodule
