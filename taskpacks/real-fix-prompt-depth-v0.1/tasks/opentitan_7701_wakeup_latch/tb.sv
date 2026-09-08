`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,sleeping_i=0,wakeup_event_i=0,clear_cause_i=0,wakeup_o;
  wakeup_latch dut(.*);always #5 clk=~clk;
  initial begin
    repeat(2)@(posedge clk);@(negedge clk);rst_n=1;sleeping_i=1;wakeup_event_i=1;
    @(posedge clk);#1;if(!wakeup_o)$fatal(1,"wakeup");
    $display("PASS");$finish;
  end
endmodule
