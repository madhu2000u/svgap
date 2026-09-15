module wakeup_latch(input logic clk,rst_n,sleeping_i,
  input logic wakeup_event_i,clear_cause_i,output logic wakeup_o);
  always_ff @(posedge clk)begin
    if(!rst_n)wakeup_o<=0;else wakeup_o<=sleeping_i&&wakeup_event_i;
  end
endmodule
