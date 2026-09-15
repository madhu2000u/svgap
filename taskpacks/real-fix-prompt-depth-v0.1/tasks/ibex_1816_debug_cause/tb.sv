`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,enter_debug_i=0,debug_req_i=0,save_cause_i=0,cause_haltreq_o;
  debug_cause dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk); rst_n=1;enter_debug_i=1;debug_req_i=1;
    @(negedge clk); enter_debug_i=0;save_cause_i=1;
    @(posedge clk); #1; if(!cause_haltreq_o) $fatal(1,"cause");
    $display("PASS");$finish;
  end
endmodule
