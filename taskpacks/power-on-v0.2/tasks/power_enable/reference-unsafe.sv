module power_enable(input logic clk, input logic rst_n, input logic load, input logic enable_in, output logic active);
  logic enabled;
  always_ff @(posedge clk) begin
    if (load) enabled <= enable_in;
  end
  always_comb if (enabled) active = 1'b1; else active = 1'b0;
endmodule
