module tb;
  logic clk;
  logic rst_n;
  logic load;
  logic enable_in;
  logic active;
  power_enable dut (.*);
  initial clk=0; always #5 clk=~clk;
  initial begin
    rst_n=0; load=0; enable_in=0;
    repeat(2) @(posedge clk);
    #1; if (active !== 1'b0) $fatal(1, "reset output");
    rst_n=1;
    @(negedge clk); load=1; enable_in=1; @(posedge clk); #1; load=0; if(active!==1) $fatal(1, "enable");
    $display("FUNCTIONAL_PASS power_enable"); $finish;
  end
endmodule
