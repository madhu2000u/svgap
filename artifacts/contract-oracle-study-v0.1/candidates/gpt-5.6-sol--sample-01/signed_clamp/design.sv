module signed_clamp(
    input  logic signed [7:0] x,
    input  logic signed [7:0] lo,
    input  logic signed [7:0] hi,
    output logic signed [7:0] y
);
    always_comb begin
        if ($signed(x) < $signed(lo))
            y = lo;
        else if ($signed(x) > $signed(hi))
            y = hi;
        else
            y = x;
    end
endmodule
