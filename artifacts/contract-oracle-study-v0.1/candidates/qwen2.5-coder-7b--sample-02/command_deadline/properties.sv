module command_deadline_properties;
  (* anyseq *) logic clk, rst_n, start;
  logic done, f_past_valid, pending;
  logic [2:0] age;
  command_deadline dut (.*);
  always_ff @(posedge clk) begin
    f_past_valid <= 1'b1;
    if (!f_past_valid) assume (!rst_n); else assume (rst_n);
    if (pending) assume (!start);
    if (!rst_n) begin pending <= 0; age <= 0; end
    else if (start && !pending) begin pending <= 1; age <= 0; end
    else if (pending && done) pending <= 0;
    else if (pending) begin assert (age < 3); age <= age + 1'b1; end
  end
endmodule
