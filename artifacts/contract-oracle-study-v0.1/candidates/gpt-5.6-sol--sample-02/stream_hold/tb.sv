`timescale 1ns/1ps
module tb;
  logic clk = 0, rst_n = 0, s_valid = 0, m_ready = 1;
  logic [7:0] s_data = 0;
  logic s_ready, m_valid;
  logic [7:0] m_data;
  stream_hold dut (.*);
  always #5 clk = ~clk;
  task send(input logic [7:0] value);
    begin
      @(negedge clk); s_valid = 1; s_data = value;
      @(posedge clk); #1;
      if (!m_valid || m_data !== value) $fatal(1, "stream mismatch");
      @(negedge clk); s_valid = 0;
    end
  endtask
  initial begin
    repeat (2) @(posedge clk); @(negedge clk); rst_n = 1;
    send(8'h25); send(8'hA6);
    $display("PASS"); $finish;
  end
endmodule
