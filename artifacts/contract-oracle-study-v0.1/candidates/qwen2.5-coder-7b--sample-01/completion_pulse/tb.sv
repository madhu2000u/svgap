`timescale 1ns/1ps
module tb;
  logic clk = 0, rst_n = 0, event_done = 0, completed;
  completion_pulse dut (.*);
  always #5 clk = ~clk;
  initial begin
    repeat (2) @(posedge clk); @(negedge clk); rst_n = 1;
    @(negedge clk); event_done = 1;
    @(posedge clk); #1; if (!completed) $fatal(1, "no completion pulse");
    @(negedge clk); event_done = 0;
    $display("PASS"); $finish;
  end
endmodule
