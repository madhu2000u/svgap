module csrng_command(input logic clk,rst_n,submit_i,
  input logic [7:0] submit_cmd_i,input logic cmd_ready_i,status_error_i,
  output logic cmd_valid_o,output logic [7:0] cmd_o,output logic error_seen_o);
  always_ff @(posedge clk) begin
    if(!rst_n) begin cmd_valid_o<=0;cmd_o<=0;error_seen_o<=0;end
    else begin
      if(status_error_i) error_seen_o<=1;
      if(cmd_valid_o&&cmd_ready_i) cmd_valid_o<=0;
      if(!cmd_valid_o&&submit_i) begin cmd_valid_o<=1;cmd_o<=submit_cmd_i;end
    end
  end
endmodule
