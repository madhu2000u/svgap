module grant_deadline_properties;
  (* anyseq *) logic clk, rst_n, request;
  logic grant, f_past_valid, pending;
  logic [1:0] age;
  grant_deadline dut (.*);
  always_ff @(posedge clk) begin
    f_past_valid <= 1'b1;
    if (!f_past_valid) assume (!rst_n); else assume (rst_n);
    if (pending) assume (!request);
    if (!rst_n) begin pending <= 0; age <= 0; end
    else if (request && !pending) begin pending <= 1; age <= 0; end
    else if (pending && grant) pending <= 0;
    else if (pending) begin assert (age < 2); age <= age + 1'b1; end
  end
endmodule
