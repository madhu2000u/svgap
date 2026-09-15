module icache_response(input logic clk, rst_n,
  input logic available_i, input logic [31:0] data_i, input logic ready_i,
  output logic valid_o, output logic [31:0] data_o);
  always_ff @(posedge clk) begin
    if (!rst_n) begin valid_o<=0; data_o<=0; end
    else if (!valid_o || ready_i) begin
      valid_o<=available_i; if (available_i) data_o<=data_i;
    end
  end
endmodule
