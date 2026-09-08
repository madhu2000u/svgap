module power_ready(input logic clk, input logic rst_n, input logic start, input logic clear, output logic ready);
  logic r;
  always_ff @(posedge clk) begin
    if (clear) r <= 1'b0;
    else if (start) r <= 1'b1;
  end
  always_comb if (r) ready = 1'b1; else ready = 1'b0;
endmodule
