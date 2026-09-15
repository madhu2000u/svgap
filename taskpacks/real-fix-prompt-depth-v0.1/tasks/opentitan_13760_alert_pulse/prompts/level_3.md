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

Required externally observable behavior: Emit one alert_o pulse on the rising edge of bad_field_i. Do not retrigger while the same bad condition remains high.

Cycle-exact contract: alert_o is high for exactly one cycle when bad_field_i transitions 0->1. It is low on the next cycle even if bad_field_i remains 1.

Verification checklist (the implementation is checked beyond examples):
- A sustained invalid encoding produces one pulse.
- A later new 0->1 event may produce another pulse.
- Reset clears the edge history and output.
