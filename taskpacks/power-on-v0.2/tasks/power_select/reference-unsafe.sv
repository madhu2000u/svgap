module power_select(input logic clk, input logic rst_n, input logic load, input logic [1:0] select_in, input logic [3:0] data_in, output logic data_out);
  logic [1:0] select;
  always_ff @(posedge clk) begin
    if (load) select <= select_in;
  end
  always_comb begin case (select) 2'd0:data_out=data_in[0]; 2'd1:data_out=data_in[1]; 2'd2:data_out=data_in[2]; default:data_out=data_in[3]; endcase end
endmodule
