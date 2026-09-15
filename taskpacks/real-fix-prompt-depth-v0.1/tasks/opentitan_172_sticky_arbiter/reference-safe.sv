module sticky_arbiter(input logic clk,rst_n,input logic [2:0] req_i,
  input logic [23:0] data_i,input logic ack_i,output logic valid_o,
  output logic [2:0] grant_o,output logic [7:0] data_o);
  always_ff @(posedge clk) begin
    if(!rst_n) begin valid_o<=0; grant_o<=0; data_o<=0; end
    else if(valid_o&&ack_i) valid_o<=0;
    else if(!valid_o) begin
      if(req_i[2]) begin valid_o<=1;grant_o<=3'b100;data_o<=data_i[23:16];end
      else if(req_i[1]) begin valid_o<=1;grant_o<=3'b010;data_o<=data_i[15:8];end
      else if(req_i[0]) begin valid_o<=1;grant_o<=3'b001;data_o<=data_i[7:0];end
    end
  end
endmodule
