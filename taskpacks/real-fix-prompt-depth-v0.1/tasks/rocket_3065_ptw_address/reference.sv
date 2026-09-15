module ptw_address(input logic[34:0]vpn_fragment_i,
  output logic[55:0]pte_addr_o);assign pte_addr_o={9'b0,vpn_fragment_i,12'b0};endmodule
