module fifo_empty_data(input logic clk,rst_n,write_i,
  input logic[7:0]data_i,input logic read_i,output logic valid_o,output logic[7:0]data_o);
  always_ff @(posedge clk)begin
    if(!rst_n)begin valid_o<=0;data_o<=0;end
    else begin if(read_i&&valid_o)valid_o<=0;if(write_i&&!valid_o)begin data_o<=data_i;valid_o<=1;end end
  end
endmodule
