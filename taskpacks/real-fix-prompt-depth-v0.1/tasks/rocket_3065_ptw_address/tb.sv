`timescale 1ns/1ps
module tb;logic[34:0]vpn_fragment_i=35'h0012345;logic[55:0]pte_addr_o;ptw_address dut(.*);
  initial begin #1;if(pte_addr_o!=={9'b0,vpn_fragment_i,12'b0})$fatal(1,"addr");
  $display("PASS");$finish;end endmodule
