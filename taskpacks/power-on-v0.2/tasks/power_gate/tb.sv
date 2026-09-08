module tb;
  logic clk, rst_n, open_gate, close_gate, din, dout;
  power_gate dut(.*);
  initial clk=0; always #5 clk=~clk;
  initial begin
    rst_n=0; open_gate=0; close_gate=0; din=1;
    repeat(2) @(posedge clk); #1; if (dout !== 1'b0) $fatal(1, "reset output");
    rst_n=1;
    @(negedge clk); open_gate=1; @(posedge clk); #1; open_gate=0;
    din=1; #1; if (dout !== 1'b1) $fatal(1, "open passes din high");
    din=0; #1; if (dout !== 1'b0) $fatal(1, "open passes din low");
    @(negedge clk); close_gate=1; @(posedge clk); #1; close_gate=0;
    din=1; #1; if (dout !== 1'b0) $fatal(1, "closed blocks din");
    $display("FUNCTIONAL_PASS power_gate"); $finish;
  end
endmodule
