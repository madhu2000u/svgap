module grant_deadline(input logic clk, input logic rst_n,
  input logic request, output logic grant);
  logic pending; logic [1:0] age;
  always_ff @(posedge clk) begin
    if (!rst_n) begin pending <= 0; age <= 0; grant <= 0; end
    else begin
      grant <= 0;
      if (request && !pending) begin pending <= 1; age <= 0; end
      else if (pending && age == 2) begin pending <= 0; grant <= 1; end
      else if (pending) age <= age + 1'b1;
    end
  end
endmodule
