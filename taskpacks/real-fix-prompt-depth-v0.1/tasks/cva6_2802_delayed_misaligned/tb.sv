`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,request_i=0,misaligned_i=0,response_o,misaligned_o;
  delayed_misaligned dut(.*);always #5 clk=~clk;
  initial begin
    repeat(2)@(posedge clk);@(negedge clk);rst_n=1;request_i=1;misaligned_i=1;
    @(posedge clk);#1;if(!response_o||!misaligned_o)$fatal(1,"response");
    $display("PASS");$finish;
  end
endmodule
