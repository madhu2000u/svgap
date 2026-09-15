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

Required externally observable behavior: After request_i, remain pending until tlb_valid_i. Pulse done_o only when the corresponding translation is valid.

Cycle-exact contract: A request starts one pending operation. While pending and tlb_valid_i=0, done_o is 0. Sampling tlb_valid_i completes it with a one-cycle done_o.

Verification checklist (the implementation is checked beyond examples):
- Arbitrary translation latency is supported.
- Stale response bits are never consumed without valid.
- New requests while pending are ignored.
