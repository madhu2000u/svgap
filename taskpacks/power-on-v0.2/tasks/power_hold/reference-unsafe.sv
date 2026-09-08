module power_hold(input logic clk, input logic rst_n, input logic en, input logic d, output logic q);
  logic held;
  always_ff @(posedge clk) begin
    if (en) held <= d;
  end
  always_comb if (held) q = 1'b1; else q = 1'b0;
endmodule
