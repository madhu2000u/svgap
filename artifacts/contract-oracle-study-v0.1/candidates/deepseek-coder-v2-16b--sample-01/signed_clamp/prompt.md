Rewrite the following reference as portable synthesizable SystemVerilog.
Preserve its exact signed and priority semantics after synthesis for every input,
including the reference behavior when `lo > hi`. Use the identical interface.

```systemverilog
module signed_clamp(
    input  logic signed [7:0] x,
    input  logic signed [7:0] lo,
    input  logic signed [7:0] hi,
    output logic signed [7:0] y
);
    always_comb begin
        if (x < lo)
            y = lo;
        else if (x > hi)
            y = hi;
        else
            y = x;
    end
endmodule
```

Return only the module, without markdown or explanation.
