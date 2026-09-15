module sticky_arbiter(input logic clk,rst_n,input logic [2:0] req_i,
  input logic [23:0] data_i,input logic ack_i,output logic valid_o,
  output logic [2:0] grant_o,output logic [7:0] data_o);
  always_comb begin
    valid_o=|req_i; grant_o=0; data_o=0;
    if(req_i[2]) begin grant_o=3'b100;data_o=data_i[23:16];end
    else if(req_i[1]) begin grant_o=3'b010;data_o=data_i[15:8];end
    else if(req_i[0]) begin grant_o=3'b001;data_o=data_i[7:0];end
  end
endmodule
