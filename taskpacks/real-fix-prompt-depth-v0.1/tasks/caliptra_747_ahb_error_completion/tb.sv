`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,transfer_i=0,done_i=0,error_i=0,dv_o;
  ahb_error_completion dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1; transfer_i=1;
    @(posedge clk); #1; if(!dv_o) $fatal(1,"dv");
    @(negedge clk); transfer_i=0; done_i=1;
    @(posedge clk); $display("PASS"); $finish;
  end
endmodule
