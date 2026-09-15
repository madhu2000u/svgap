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

Required externally observable behavior: Implement a one-entry FIFO. When empty, valid_o is zero and data_o is zero; when full, data_o is the stored byte until it is read.

Cycle-exact contract: write_i while empty stores data_i and sets valid. read_i while valid clears valid. data_o is stored_data only when valid, otherwise exactly 8'h00.
