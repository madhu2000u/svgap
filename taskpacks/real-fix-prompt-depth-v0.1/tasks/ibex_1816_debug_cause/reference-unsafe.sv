module debug_cause(input logic clk,rst_n,enter_debug_i,
  input logic debug_req_i,save_cause_i,output logic cause_haltreq_o);
  always_ff @(posedge clk) begin
    if(!rst_n) cause_haltreq_o<=0;
    else if(save_cause_i) cause_haltreq_o<=debug_req_i;
  end
endmodule
