You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module fifo_empty_data(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       write_i,
    input  logic [7:0] data_i,
    input  logic       read_i,
    output logic       valid_o,
    output logic [7:0] data_o
);
```

Issue-style context: A one-entry FIFO correctly dropped valid after its last read but continued to expose the stale dequeued byte on its data output.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.
