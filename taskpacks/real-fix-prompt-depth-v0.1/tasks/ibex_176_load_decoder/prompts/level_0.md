You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module load_decoder(
    input  logic [6:0] opcode_i,
    input  logic [2:0] funct3_i,
    output logic       valid_load_o,
    output logic       illegal_o
);
```

Issue-style context: The unsupported LWU funct3 encoding was accepted as a normal load instead of being marked illegal.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.
