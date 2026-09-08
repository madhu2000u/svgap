You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module alert_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic bad_field_i,
    output logic alert_o
);
```

Issue-style context: A recoverable alert was driven as a level from a latched invalid-field condition, repeatedly alerting for one software error.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.
