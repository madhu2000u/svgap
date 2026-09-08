module iti_valid(input logic enable_i,input logic[1:0]slot_valid_i,
  output logic valid_o);always_comb valid_o=enable_i&&(|slot_valid_i);endmodule
