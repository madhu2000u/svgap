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
