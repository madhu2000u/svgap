module tile_widths(input logic[15:0]hart_id_i,input logic[47:0]reset_vector_i,
  output logic[15:0]tile_hart_id_o,output logic[47:0]tile_reset_vector_o);
  assign tile_hart_id_o=hart_id_i;assign tile_reset_vector_o=reset_vector_i;
endmodule
