module power_enable(input logic clk, input logic rst_n, input logic load, input logic enable_in, output logic active);
  logic enabled;
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) enabled <= 1'b0;
    else if (load) enabled <= enable_in;
  end
  always_comb if (enabled) active = 1'b1; else active = 1'b0;
endmodule
