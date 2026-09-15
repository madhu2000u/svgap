You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module rom_kmac_counter(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       word_valid_i,
    input  logic       kmac_ready_i,
    output logic [7:0] addr_o
);
```

Issue-style context: After KMAC released backpressure, the ROM stream address remained on the accepted word for one extra cycle and fetched it twice.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Advance the ROM address once for each valid/ready word handshake, including the first handshake after a stall.

Cycle-exact contract: If word_valid_i&&kmac_ready_i is sampled, addr_o in the following cycle equals its previous value plus one; otherwise a pending word does not advance.
