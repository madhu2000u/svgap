module icache_response(input logic clk, rst_n,
  input logic available_i, input logic [31:0] data_i, input logic ready_i,
  output logic valid_o, output logic [31:0] data_o);
  logic stored; logic [31:0] stored_data;
  always_ff @(posedge clk) begin
    if (!rst_n) begin stored<=0; stored_data<=0; end
    else if (available_i) begin stored<=1; stored_data<=data_i; end
    else if (ready_i) stored<=0;
  end
  assign valid_o=stored && ready_i; assign data_o=stored_data;
endmodule
