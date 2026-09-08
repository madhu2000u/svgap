You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module icache_response(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        available_i,
    input  logic [31:0] data_i,
    input  logic        ready_i,
    output logic        valid_o,
    output logic [31:0] data_o
);
```

Issue-style context: A completed instruction response could be withheld while the consumer was not ready, coupling response availability to acceptance.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Buffer each available response. Assert valid as soon as it is buffered, independent of ready, and retain the response until accepted.
