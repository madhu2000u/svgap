module command_deadline(input logic clk, input logic rst_n,
  input logic start, output logic done);
  logic busy; logic [1:0] age;
  always_ff @(posedge clk) begin
    if (!rst_n) begin busy <= 0; age <= 0; done <= 0; end
    else begin
      done <= 0;
      if (start && !busy) begin busy <= 1; age <= 0; end
      else if (busy && age == 2) begin busy <= 0; done <= 1; end
      else if (busy) age <= age + 1'b1;
    end
  end
endmodule
