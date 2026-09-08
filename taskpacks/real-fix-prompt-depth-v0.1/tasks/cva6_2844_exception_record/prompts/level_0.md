You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module exception_record(
    input  logic        illegal_i,
    input  logic        virt_i,
    input  logic [31:0] instr_i,
    output logic        valid_o,
    output logic [5:0]  cause_o,
    output logic [31:0] tval_o,
    output logic [31:0] htval_o,
    output logic [31:0] mtinst_o,
    output logic        gva_o
);
```

Issue-style context: An illegal custom-instruction path left hypervisor exception fields undefined, allowing arbitrary transformed-instruction metadata.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.
