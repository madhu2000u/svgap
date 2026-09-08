`timescale 1ns/1ps
module tb;
  logic[15:0]hart_id_i=16'h0034,tile_hart_id_o;
  logic[47:0]reset_vector_i=48'h0000_8000_0000,tile_reset_vector_o;tile_widths dut(.*);
  initial begin #1;if(tile_hart_id_o!==hart_id_i||tile_reset_vector_o!==reset_vector_i)$fatal(1,"width");
    $display("PASS");$finish;end
endmodule
