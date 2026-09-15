`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,word_valid_i=0,word_ready_i=1,window_last_i=0,process_o;
  conditioner_done dut(.*);always #5 clk=~clk;
  initial begin
    repeat(2)@(posedge clk);@(negedge clk);rst_n=1;word_valid_i=1;window_last_i=1;
    @(posedge clk);#1;if(!process_o)$fatal(1,"process");
    $display("PASS");$finish;
  end
endmodule
