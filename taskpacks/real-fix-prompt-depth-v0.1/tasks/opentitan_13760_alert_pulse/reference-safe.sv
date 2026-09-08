module alert_pulse(input logic clk,rst_n,bad_field_i,output logic alert_o);
  logic bad_q;always_ff @(posedge clk)begin
    if(!rst_n)begin bad_q<=0;alert_o<=0;end
    else begin alert_o<=bad_field_i&&!bad_q;bad_q<=bad_field_i;end
  end
endmodule
