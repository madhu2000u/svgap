module conditioner_done(input logic clk,rst_n,word_valid_i,
  input logic word_ready_i,window_last_i,output logic process_o);
  always_ff @(posedge clk)begin
    if(!rst_n)process_o<=0;else process_o<=word_valid_i&&word_ready_i&&window_last_i;
  end
endmodule
