You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module itlb_wait(
    input  logic clk,
    input  logic rst_n,
    input  logic request_i,
    input  logic tlb_valid_i,
    output logic pending_o,
    output logic done_o
);
```

Issue-style context: An MMIO fetch state machine could leave its translation step before the current iTLB response was valid.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.
