You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module masked_packer(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       valid_i,
    input  logic [7:0] data_i,
    input  logic [3:0] mask_i,
    output logic       ready_o,
    output logic       valid_o,
    output logic [7:0] data_o,
    input  logic       ready_i
);
```

Issue-style context: A full packed word could stop appearing valid and upstream ready could remain asserted when the downstream interface was stalled.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Treat an all-masked input as one complete buffered word. Hold the word and apply upstream backpressure until it is accepted.
