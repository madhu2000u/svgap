module axi_sub_arbiter(input logic clk,rst_n,
  input logic read_valid_i,input logic [15:0] read_addr_i,
  input logic write_valid_i,input logic [15:0] write_addr_i,input logic out_ready_i,
  output logic out_valid_o,out_is_write_o,output logic [15:0] out_addr_o);
  always_ff @(posedge clk) begin
    if(!rst_n) begin out_valid_o<=0; out_is_write_o<=0; out_addr_o<=0; end
    else if(out_valid_o && out_ready_i) out_valid_o<=0;
    else if(!out_valid_o) begin
      if(write_valid_i) begin out_valid_o<=1; out_is_write_o<=1; out_addr_o<=write_addr_i; end
      else if(read_valid_i) begin out_valid_o<=1; out_is_write_o<=0; out_addr_o<=read_addr_i; end
    end
  end
endmodule
