`timescale 1ns/1ps
module tb;
  logic [7:0] a, b, y; logic [2:0] op;
  opcode_unit dut (.*);
  task check(input logic [2:0] code, input logic [7:0] av, bv, expected);
    begin op = code; a = av; b = bv; #1; if (y !== expected) $fatal(1, "opcode mismatch"); end
  endtask
  initial begin
    check(0, 8'h12, 8'h05, 8'h17);
    check(1, 8'h12, 8'h05, 8'h0d);
    check(2, 8'hac, 8'h66, 8'h24);
    $display("PASS"); $finish;
  end
endmodule
