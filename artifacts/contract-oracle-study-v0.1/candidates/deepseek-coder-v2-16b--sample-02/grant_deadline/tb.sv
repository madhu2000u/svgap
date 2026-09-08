`timescale 1ns/1ps
module tb;
  logic clk = 0, rst_n = 0, request = 0, grant;
  grant_deadline dut (.*);
  always #5 clk = ~clk;
  initial begin
    repeat (2) @(posedge clk); rst_n = 1;
    @(negedge clk); request = 1; @(negedge clk); request = 0;
    repeat (6) begin @(posedge clk); #1; if (grant) begin $display("PASS"); $finish; end end
    $fatal(1, "no grant");
  end
endmodule
