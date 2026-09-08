You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module iti_valid(
    input  logic       enable_i,
    input  logic [1:0] slot_valid_i,
    output logic       valid_o
);
```

Issue-style context: Incomplete combinational assignment inferred a latch, allowing an instruction-trace valid bit to retain a previous cycle's value.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.
