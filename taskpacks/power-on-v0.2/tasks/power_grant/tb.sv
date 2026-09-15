module tb;
  logic clk, rst_n, req, done, grant;
  power_grant dut(.*);
  initial clk=0; always #5 clk=~clk;
  initial begin
    rst_n=0; req=0; done=0;
    repeat(2) @(posedge clk); #1; if (grant !== 1'b0) $fatal(1, "reset output");
    rst_n=1;
    @(negedge clk); req=1; @(posedge clk); #1; req=0; if (grant !== 1'b1) $fatal(1, "grant on req");
    @(negedge clk); done=1; @(posedge clk); #1; done=0; if (grant !== 1'b0) $fatal(1, "release on done");
    $display("FUNCTIONAL_PASS power_grant"); $finish;
  end
endmodule
