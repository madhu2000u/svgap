You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module axi_sub_arbiter(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        read_valid_i,
    input  logic [15:0] read_addr_i,
    input  logic        write_valid_i,
    input  logic [15:0] write_addr_i,
    input  logic        out_ready_i,
    output logic        out_valid_o,
    output logic        out_is_write_o,
    output logic [15:0] out_addr_o
);
```

Issue-style context: A newly arriving write could replace a previously selected read while the shared downstream request was stalled.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Apply write-over-read priority only when choosing a new beat. Latch the winner and its address until the downstream transfer is accepted.

Cycle-exact contract: For every cycle after out_valid_o&&!out_ready_i, out_valid_o, out_is_write_o, and out_addr_o remain unchanged until acceptance.
