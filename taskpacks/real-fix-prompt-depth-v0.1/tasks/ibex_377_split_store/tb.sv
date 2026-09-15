`timescale 1ns/1ps
module tb;
  logic clk=0,rst_n=0,start_i=0,first_done_i=0,first_error_i=0,second_done_i=0;
  logic second_req_o,complete_o,fault_o; split_store dut(.*); always #5 clk=~clk;
  initial begin
    repeat(2) @(posedge clk); @(negedge clk);rst_n=1;start_i=1;
    @(negedge clk);start_i=0;first_done_i=1;
    @(posedge clk);#1;if(!second_req_o)$fatal(1,"second");
    @(negedge clk);first_done_i=0;second_done_i=1;
    @(posedge clk);#1;if(!complete_o||fault_o)$fatal(1,"complete");
    $display("PASS");$finish;
  end
endmodule
