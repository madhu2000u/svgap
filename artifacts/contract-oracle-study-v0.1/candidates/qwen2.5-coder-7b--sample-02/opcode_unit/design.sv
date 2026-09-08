module opcode_unit(
    input  logic [7:0] a,
    input  logic [7:0] b,
    input  logic [2:0] op,
    output logic [7:0] y
);
    always_comb begin
        case (op)
            3'd0: y = a + b;
            3'd1: y = a - b;
            3'd2: y = a & b;
            3'd3: y = a | b;
            3'd4: y = a ^ b;
            3'd5: y = a << b[2:0];
            3'd6: y = a >> b[2:0];
            default: y = (a < b) ? 8'h01 : 8'h00;
        endcase
    end
endmodule
