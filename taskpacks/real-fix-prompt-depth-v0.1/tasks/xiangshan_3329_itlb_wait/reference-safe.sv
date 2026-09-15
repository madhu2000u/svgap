module itlb_wait(input logic clk,rst_n,request_i,tlb_valid_i,
  output logic pending_o,done_o);
  always_ff @(posedge clk)begin
    if(!rst_n)begin pending_o<=0;done_o<=0;end
    else begin done_o<=0;if(!pending_o&&request_i)pending_o<=1;
      else if(pending_o&&tlb_valid_i)begin pending_o<=0;done_o<=1;end end
  end
endmodule
