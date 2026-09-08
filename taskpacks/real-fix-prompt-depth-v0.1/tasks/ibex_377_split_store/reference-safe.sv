module split_store(input logic clk,rst_n,start_i,first_done_i,
  input logic first_error_i,second_done_i,output logic second_req_o,complete_o,fault_o);
  logic active,error_q;
  always_ff @(posedge clk) begin
    if(!rst_n) begin active<=0;error_q<=0;second_req_o<=0;complete_o<=0;fault_o<=0;end
    else begin
      complete_o<=0;fault_o<=0;
      if(start_i&&!active) begin active<=1;error_q<=0;end
      if(active&&first_done_i) begin second_req_o<=1;error_q<=first_error_i;end
      if(active&&second_req_o&&second_done_i) begin
        active<=0;second_req_o<=0;complete_o<=1;fault_o<=error_q;
      end
    end
  end
endmodule
