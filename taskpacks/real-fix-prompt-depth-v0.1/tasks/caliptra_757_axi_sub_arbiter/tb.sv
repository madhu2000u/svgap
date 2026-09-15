`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,read_valid_i=0,write_valid_i=0,out_ready_i=1;
  logic [15:0] read_addr_i=0,write_addr_i=0,out_addr_o;
  logic out_valid_o,out_is_write_o;
  axi_sub_arbiter dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1;
    read_valid_i=1; read_addr_i=16'h1234;
    @(posedge clk); #1; if(!out_valid_o || out_is_write_o || out_addr_o!==16'h1234) $fatal(1,"arb");
    $display("PASS"); $finish;
  end
endmodule
