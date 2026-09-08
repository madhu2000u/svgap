module stream_hold_properties;
  (* anyseq *) logic clk, rst_n, s_valid, m_ready;
  (* anyseq *) logic [7:0] s_data;
  logic s_ready, m_valid;
  logic [7:0] m_data;
  logic f_past_valid;
  stream_hold dut (.*);
  always_ff @(posedge clk) begin
    f_past_valid <= 1'b1;
    if (!f_past_valid) assume (!rst_n); else assume (rst_n);
    if (f_past_valid && $past(rst_n && m_valid && !m_ready)) begin
      assert (m_valid);
      assert (m_data == $past(m_data));
    end
  end
endmodule
