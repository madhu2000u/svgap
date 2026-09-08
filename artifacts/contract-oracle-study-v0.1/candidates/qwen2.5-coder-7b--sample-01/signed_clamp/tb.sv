`timescale 1ns/1ps
module tb;
  logic signed [7:0] x, lo, hi, y;
  signed_clamp dut (.*);
  task check(input integer xv, lv, hv, expected);
    begin x=xv; lo=lv; hi=hv; #1; if (y !== expected[7:0]) $fatal(1, "clamp mismatch"); end
  endtask
  initial begin
    check(-20, -10, 30, -10); check(40, -10, 30, 30); check(5, -10, 30, 5);
    $display("PASS"); $finish;
  end
endmodule
