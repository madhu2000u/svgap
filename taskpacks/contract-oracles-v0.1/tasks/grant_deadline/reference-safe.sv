module grant_deadline(input logic clk, input logic rst_n,
  input logic request, output logic grant);
  logic pending;
  always_ff @(posedge clk) begin
    if (!rst_n) begin pending <= 0; grant <= 0; end
    else begin
      grant <= 0;
      if (request && !pending) pending <= 1;
      else if (pending) begin pending <= 0; grant <= 1; end
    end
  end
endmodule
