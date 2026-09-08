You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module conditioner_done(
    input  logic clk,
    input  logic rst_n,
    input  logic word_valid_i,
    input  logic word_ready_i,
    input  logic window_last_i,
    output logic process_o
);
```

Issue-style context: A health-test window completion could start conditioning before its final FIFO word had actually been accepted.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Pulse process_o only when the word marked window_last_i completes a word_valid_i/word_ready_i handshake.

Cycle-exact contract: process_o in cycle N+1 equals word_valid_i&&word_ready_i&&window_last_i sampled in cycle N. Merely presenting an unaccepted final word is insufficient.
