module result_hold_properties;
  (* anyseq *) logic clk, rst_n, produce, result_ready;
  (* anyseq *) logic [15:0] result_in;
  logic produce_ready, result_valid;
  logic [15:0] result_out;
  logic f_past_valid;
  result_hold dut (.*);
  always_ff @(posedge clk) begin
    f_past_valid <= 1'b1;
    if (!f_past_valid) assume (!rst_n); else assume (rst_n);
    if (f_past_valid && $past(rst_n && result_valid && !result_ready)) begin
      assert (result_valid);
      assert (result_out == $past(result_out));
    end
  end
endmodule
