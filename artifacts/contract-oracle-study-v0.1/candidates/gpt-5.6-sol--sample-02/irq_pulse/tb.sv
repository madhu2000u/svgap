`timescale 1ns/1ps
module tb;
  logic clk = 0, rst_n = 0, trigger = 0, irq;
  irq_pulse dut (.*);
  always #5 clk = ~clk;
  initial begin
    repeat (2) @(posedge clk); @(negedge clk); rst_n = 1;
    @(negedge clk); trigger = 1;
    @(posedge clk); #1; if (!irq) $fatal(1, "no interrupt");
    @(negedge clk); trigger = 0;
    $display("PASS"); $finish;
  end
endmodule
