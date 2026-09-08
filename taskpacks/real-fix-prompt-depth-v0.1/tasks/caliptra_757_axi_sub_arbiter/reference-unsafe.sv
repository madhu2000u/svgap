module axi_sub_arbiter(input logic clk,rst_n,
  input logic read_valid_i,input logic [15:0] read_addr_i,
  input logic write_valid_i,input logic [15:0] write_addr_i,input logic out_ready_i,
  output logic out_valid_o,out_is_write_o,output logic [15:0] out_addr_o);
  always_comb begin
    out_valid_o=write_valid_i||read_valid_i;
    out_is_write_o=write_valid_i;
    out_addr_o=write_valid_i?write_addr_i:read_addr_i;
  end
endmodule
