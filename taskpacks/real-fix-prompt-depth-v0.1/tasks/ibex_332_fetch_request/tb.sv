`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,start_i=0,redirect_i=0,gnt_i=0,req_o;
  logic [31:0] start_addr_i=0,redirect_addr_i=0,addr_o;
  fetch_request dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1;
    @(negedge clk); start_i=1; start_addr_i=32'h1000;
    @(posedge clk); #1; if(!req_o || addr_o!==32'h1000) $fatal(1,"request");
    @(negedge clk); start_i=0; gnt_i=1;
    @(posedge clk); $display("PASS"); $finish;
  end
endmodule
