module completion_pulse(input logic clk, input logic rst_n,
  input logic event_done, output logic completed);
  logic delayed;
  always_ff @(posedge clk) begin
    if (!rst_n) begin completed <= 0; delayed <= 0; end
    else begin delayed <= event_done; completed <= event_done || delayed; end
  end
endmodule
