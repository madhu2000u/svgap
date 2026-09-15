`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,submit_i=0,cmd_ready_i=1,status_error_i=0;
  logic cmd_valid_o,error_seen_o; logic [7:0] submit_cmd_i=0,cmd_o;
  csrng_command dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1; submit_i=1; submit_cmd_i=8'hA7;
    @(posedge clk); #1; if(!cmd_valid_o || cmd_o!==8'hA7) $fatal(1,"cmd");
    $display("PASS"); $finish;
  end
endmodule
