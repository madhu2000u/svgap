module power_mode(input logic clk, input logic rst_n, input logic load, input logic mode_in, input logic data_in, output logic data_out);
  logic mode;
  always_ff @(posedge clk) begin
    if (load) mode <= mode_in;
  end
  always_comb if (mode) data_out = data_in; else data_out = 1'b0;
endmodule
