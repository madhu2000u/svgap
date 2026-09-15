module tb;
  logic clk;
  logic rst_n;
  logic load;
  logic valid_in;
  logic payload_in;
  logic payload_out;
  power_valid dut (.*);
  initial clk=0; always #5 clk=~clk;
  initial begin
    rst_n=0; load=0; valid_in=0; payload_in=0;
    repeat(2) @(posedge clk);
    #1; if (payload_out !== 1'b0) $fatal(1, "reset output");
    rst_n=1;
    @(negedge clk); load=1; valid_in=1; payload_in=1; @(posedge clk); #1; load=0; if(payload_out!==1) $fatal(1, "valid");
    $display("FUNCTIONAL_PASS power_valid"); $finish;
  end
endmodule
