module alert_pulse(input logic clk,rst_n,bad_field_i,output logic alert_o);
  always_ff @(posedge clk)begin if(!rst_n)alert_o<=0;else alert_o<=bad_field_i;end
endmodule
