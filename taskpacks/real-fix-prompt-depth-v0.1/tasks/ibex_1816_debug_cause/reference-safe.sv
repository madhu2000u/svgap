module debug_cause(input logic clk,rst_n,enter_debug_i,
  input logic debug_req_i,save_cause_i,output logic cause_haltreq_o);
  logic entry_haltreq;
  always_ff @(posedge clk) begin
    if(!rst_n) begin entry_haltreq<=0;cause_haltreq_o<=0;end
    else begin
      if(enter_debug_i) entry_haltreq<=debug_req_i;
      if(save_cause_i) cause_haltreq_o<=entry_haltreq;
    end
  end
endmodule
