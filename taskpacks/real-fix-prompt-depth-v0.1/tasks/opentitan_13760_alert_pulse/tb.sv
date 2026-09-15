`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,bad_field_i=0,alert_o;alert_pulse dut(.*);always #5 clk=~clk;
  initial begin
    repeat(2)@(posedge clk);@(negedge clk);rst_n=1;bad_field_i=1;
    @(posedge clk);#1;if(!alert_o)$fatal(1,"alert");
    $display("PASS");$finish;
  end
endmodule
