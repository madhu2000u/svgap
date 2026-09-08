module result_hold(
  input logic clk, input logic rst_n, input logic produce,
  input logic [15:0] result_in, output logic produce_ready,
  output logic result_valid, output logic [15:0] result_out,
  input logic result_ready
);
  assign produce_ready = !result_valid || result_ready;
  always_ff @(posedge clk) begin
    if (!rst_n) begin result_valid <= 0; result_out <= 0; end
    else if (produce_ready) begin
      result_valid <= produce;
      if (produce) result_out <= result_in;
    end
  end
endmodule
