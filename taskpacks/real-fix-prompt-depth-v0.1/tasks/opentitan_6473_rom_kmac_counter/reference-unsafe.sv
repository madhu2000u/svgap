module rom_kmac_counter(input logic clk,rst_n,word_valid_i,
  input logic kmac_ready_i,output logic [7:0] addr_o);
  logic advance_q;
  always_ff @(posedge clk) begin
    if(!rst_n) begin addr_o<=0; advance_q<=0; end
    else begin advance_q<=word_valid_i&&kmac_ready_i; if(advance_q) addr_o<=addr_o+1'b1; end
  end
endmodule
