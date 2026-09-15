module power_valid(input logic clk, input logic rst_n, input logic load, input logic valid_in, input logic payload_in, output logic payload_out);
  logic valid; logic payload;
  always_ff @(posedge clk) begin
    if (load) begin valid <= valid_in; payload <= payload_in; end
  end
  always_comb if (valid) payload_out = payload; else payload_out = 1'b0;
endmodule
