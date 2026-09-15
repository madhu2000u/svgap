module tile_widths(input logic[15:0]hart_id_i,input logic[47:0]reset_vector_i,
  output logic[15:0]tile_hart_id_o,output logic[47:0]tile_reset_vector_o);
  assign tile_hart_id_o={8'b0,hart_id_i[7:0]};
  assign tile_reset_vector_o={16'b0,reset_vector_i[31:0]};
endmodule
