You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module range_priority(
    input  logic [7:0] addr_i,
    input  logic       read_i,
    input  logic       en0_i,
    input  logic [7:0] lo0_i,
    input  logic [7:0] hi0_i,
    input  logic       allow_r0_i,
    input  logic       allow_w0_i,
    input  logic       en1_i,
    input  logic [7:0] lo1_i,
    input  logic [7:0] hi1_i,
    input  logic       allow_r1_i,
    input  logic       allow_w1_i,
    output logic       matched_o,
    output logic       allow_o,
    output logic       index_o
);
```

Issue-style context: An overlapping lower-priority access-control range could override the per-access permission of the lower-index winning range.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Choose the first enabled matching range, index 0 before index 1. Use only that range's read or write permission for the requested access type.

Cycle-exact contract: match0=en0_i&&addr_i in [lo0_i,hi0_i]; match1 similarly. If match0, index_o=0 and allow_o=read_i?allow_r0_i:allow_w0_i. Else use range1.

Verification checklist (the implementation is checked beyond examples):
- Overlapping ranges never combine permissions.
- Lowest index has priority independently for reads and writes.
- No match yields matched_o=0 and allow_o=0.
