Write a synthesizable SystemVerilog module with exactly this interface:

```systemverilog
module result_hold(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        produce,
    input  logic [15:0] result_in,
    output logic        produce_ready,
    output logic        result_valid,
    output logic [15:0] result_out,
    input  logic        result_ready
);
```

Implement one-entry decoupling storage. Accept `produce/result_in` only when
`produce && produce_ready`. Present it with `result_valid/result_out`. While
`result_valid && !result_ready`, keep `result_valid` asserted and keep
`result_out` bit-for-bit stable until acceptance. Permit replacement on the
same cycle an old result is accepted. Reset is synchronous active-low and
clears valid. Use portable synthesizable RTL.

Return only the module.
