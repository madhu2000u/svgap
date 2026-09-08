module iti_valid(input logic enable_i,input logic[1:0]slot_valid_i,
  output logic valid_o);assign valid_o=|slot_valid_i;endmodule
