`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,word_valid_i=0,kmac_ready_i=0; logic [7:0] addr_o;
  rom_kmac_counter dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1;
    word_valid_i=1; kmac_ready_i=1;
    @(posedge clk); $display("PASS"); $finish;
  end
endmodule
