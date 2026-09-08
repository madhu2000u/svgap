module tb;
  logic clk, rst_n, start, clear, ready;
  power_ready dut(.*);
  initial clk=0; always #5 clk=~clk;
  initial begin
    rst_n=0; start=0; clear=0;
    repeat(2) @(posedge clk); #1; if (ready !== 1'b0) $fatal(1, "reset output");
    rst_n=1;
    @(negedge clk); start=1; @(posedge clk); #1; start=0; if (ready !== 1'b1) $fatal(1, "start");
    @(negedge clk); clear=1; @(posedge clk); #1; clear=0; if (ready !== 1'b0) $fatal(1, "clear");
    $display("FUNCTIONAL_PASS power_ready"); $finish;
  end
endmodule
