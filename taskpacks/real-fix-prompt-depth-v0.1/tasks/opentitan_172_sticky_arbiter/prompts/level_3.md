You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module sticky_arbiter(
    input  logic        clk,
    input  logic        rst_n,
    input  logic [2:0]  req_i,
    input  logic [23:0] data_i,
    input  logic        ack_i,
    output logic        valid_o,
    output logic [2:0]  grant_o,
    output logic [7:0]  data_o
);
```

Issue-style context: A later higher-priority request could replace the requester and data of an already-selected transfer before acknowledgement.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Select the highest active requester when idle, then hold the one-hot grant and selected data until ack_i.

Cycle-exact contract: Whenever valid_o&&!ack_i is sampled, valid_o, grant_o, and data_o remain bit-for-bit stable in the next cycle.

Verification checklist (the implementation is checked beyond examples):
- A stalled selection is sticky.
- New priority decisions occur only when no transfer is pending.
- grant_o is one-hot whenever valid_o is asserted.
