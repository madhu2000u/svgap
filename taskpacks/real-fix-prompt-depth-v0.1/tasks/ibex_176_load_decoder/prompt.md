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

Required externally observable behavior: For load opcode 7'b0000011, accept funct3 000,001,010,100,101 only. All other funct3 encodings, including 110, are illegal.

Cycle-exact contract: valid_load_o is one exactly for the five supported load encodings. illegal_o is one for unsupported funct3 under the load opcode and zero otherwise.
