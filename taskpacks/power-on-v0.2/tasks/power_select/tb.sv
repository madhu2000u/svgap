module tb;
  logic clk;
  logic rst_n;
  logic load;
  logic [1:0] select_in;
  logic [3:0] data_in;
  logic data_out;
  power_select dut (.*);
  initial clk=0; always #5 clk=~clk;
  initial begin
    rst_n=0; load=0; select_in=0; data_in=0;
    repeat(2) @(posedge clk);
    #1; if (data_out !== 1'b0) $fatal(1, "reset output");
    rst_n=1;
    @(negedge clk); load=1; select_in=2; data_in=4'b0100; @(posedge clk); #1; load=0; if(data_out!==1) $fatal(1, "select");
    $display("FUNCTIONAL_PASS power_select"); $finish;
  end
endmodule
