`timescale 1ns/1ps
module tb;
  logic clk = 0, rst_n = 0, start = 0, done;
  command_deadline dut (.*);
  always #5 clk = ~clk;
  initial begin
    repeat (2) @(posedge clk); rst_n = 1;
    @(negedge clk); start = 1; @(negedge clk); start = 0;
    repeat (8) begin @(posedge clk); #1; if (done) begin $display("PASS"); $finish; end end
    $fatal(1, "no completion");
  end
endmodule
