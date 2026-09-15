You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module wakeup_latch(
    input  logic clk,
    input  logic rst_n,
    input  logic sleeping_i,
    input  logic wakeup_event_i,
    input  logic clear_cause_i,
    output logic wakeup_o
);
```

Issue-style context: A timer wakeup request could drop when sleep ended even though software had not cleared the recorded wakeup cause.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Latch each wakeup_event_i and keep wakeup_o asserted until clear_cause_i, independent of the current sleeping_i value.

Cycle-exact contract: A sampled wakeup_event_i sets wakeup_o. Once set, wakeup_o stays high on every cycle until clear_cause_i is sampled.

Verification checklist (the implementation is checked beyond examples):
- Leaving sleep cannot acknowledge a wakeup.
- Only clear_cause_i or reset clears the latched request.
- Events are not lost if sleep state changes immediately.
