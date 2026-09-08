module wakeup_latch(input logic clk,rst_n,sleeping_i,
  input logic wakeup_event_i,clear_cause_i,output logic wakeup_o);
  always_ff @(posedge clk)begin
    if(!rst_n)wakeup_o<=0;else if(clear_cause_i)wakeup_o<=0;else if(wakeup_event_i)wakeup_o<=1;
  end
endmodule
