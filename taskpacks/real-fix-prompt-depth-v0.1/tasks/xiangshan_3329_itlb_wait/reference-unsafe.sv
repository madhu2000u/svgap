module itlb_wait(input logic clk,rst_n,request_i,tlb_valid_i,
  output logic pending_o,done_o);
  always_ff @(posedge clk)begin
    if(!rst_n)begin pending_o<=0;done_o<=0;end
    else begin done_o<=pending_o;if(request_i)pending_o<=1;else if(pending_o)pending_o<=0;end
  end
endmodule
