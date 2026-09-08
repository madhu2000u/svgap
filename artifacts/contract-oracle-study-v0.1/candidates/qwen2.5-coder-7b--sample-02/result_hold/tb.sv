`timescale 1ns/1ps
module tb;
  logic clk = 0, rst_n = 0, produce = 0, result_ready = 1;
  logic [15:0] result_in = 0;
  logic produce_ready, result_valid;
  logic [15:0] result_out;
  result_hold dut (.*);
  always #5 clk = ~clk;
  task send(input logic [15:0] value);
    begin
      @(negedge clk); produce = 1; result_in = value;
      @(posedge clk); #1;
      if (!result_valid || result_out !== value) $fatal(1, "result mismatch");
      @(negedge clk); produce = 0;
    end
  endtask
  initial begin
    repeat (2) @(posedge clk); @(negedge clk); rst_n = 1;
    send(16'h1234); send(16'hBEEF);
    $display("PASS"); $finish;
  end
endmodule
