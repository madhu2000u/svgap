module tb;
  logic clk, rst_n, en, d, q;
  power_hold dut(.*);
  initial clk=0; always #5 clk=~clk;
  initial begin
    rst_n=0; en=0; d=0;
    repeat(2) @(posedge clk); #1; if (q !== 1'b0) $fatal(1, "reset output");
    rst_n=1;
    @(negedge clk); en=1; d=1; @(posedge clk); #1; en=0; if (q !== 1'b1) $fatal(1, "capture one");
    @(negedge clk); en=1; d=0; @(posedge clk); #1; en=0; if (q !== 1'b0) $fatal(1, "capture zero");
    $display("FUNCTIONAL_PASS power_hold"); $finish;
  end
endmodule
