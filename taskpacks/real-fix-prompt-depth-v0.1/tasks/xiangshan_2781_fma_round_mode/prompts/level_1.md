You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module fma_round_mode(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       issue_i,
    input  logic [2:0] rm_i,
    input  logic       complete_i,
    output logic [2:0] rm_used_o
);
```

Issue-style context: A multi-stage FMA could use a newer live rounding mode in its add stage instead of the mode present when the instruction issued.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Capture rm_i at issue_i and report that captured mode when complete_i finishes the same in-flight operation.
