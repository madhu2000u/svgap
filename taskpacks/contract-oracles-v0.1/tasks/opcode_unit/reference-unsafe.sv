module opcode_unit(input logic [7:0] a, input logic [7:0] b,
  input logic [2:0] op, output logic [7:0] y);
  always_comb case (op)
    0: y=a+b; 1: y=a-b; 2: y=a&b; 3: y=a|b; 4: y=a^b;
    5: y=a<<b[2:0]; 6: y=a>>b[2:0]; default: y=(a>b)?1:0;
  endcase
endmodule
