module power_grant(input logic clk, input logic rst_n, input logic req, input logic done, output logic grant);
  logic g;
  always_ff @(posedge clk) begin
    if (done) g <= 1'b0;
    else if (req) g <= 1'b1;
  end
  always_comb if (g) grant = 1'b1; else grant = 1'b0;
endmodule
