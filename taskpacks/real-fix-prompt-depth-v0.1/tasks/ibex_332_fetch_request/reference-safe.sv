module fetch_request(input logic clk,rst_n,start_i,
  input logic [31:0] start_addr_i,input logic redirect_i,
  input logic [31:0] redirect_addr_i,input logic gnt_i,
  output logic req_o,output logic [31:0] addr_o);
  always_ff @(posedge clk) begin
    if(!rst_n) begin req_o<=0; addr_o<=0; end
    else if(!req_o && start_i) begin req_o<=1; addr_o<=start_addr_i; end
    else if(req_o && gnt_i) req_o<=0;
  end
endmodule
