module rom_kmac_counter(input logic clk,rst_n,word_valid_i,
  input logic kmac_ready_i,output logic [7:0] addr_o);
  always_ff @(posedge clk) begin
    if(!rst_n) addr_o<=0; else if(word_valid_i&&kmac_ready_i) addr_o<=addr_o+1'b1;
  end
endmodule
