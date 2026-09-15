module power_gate(input logic clk, input logic rst_n, input logic open_gate, input logic close_gate, input logic din, output logic dout);
  logic gate;
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) gate <= 1'b0;
    else if (close_gate) gate <= 1'b0;
    else if (open_gate) gate <= 1'b1;
  end
  always_comb if (gate) dout = din; else dout = 1'b0;
endmodule
