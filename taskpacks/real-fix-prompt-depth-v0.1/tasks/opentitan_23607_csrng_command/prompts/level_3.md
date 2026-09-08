You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module csrng_command(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       submit_i,
    input  logic [7:0] submit_cmd_i,
    input  logic       cmd_ready_i,
    input  logic       status_error_i,
    output logic       cmd_valid_o,
    output logic [7:0] cmd_o,
    output logic       error_seen_o
);
```

Issue-style context: An acknowledge-status error could cancel a pending CSRNG command while the receiver was still applying backpressure.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Hold command valid and payload until ready completes the handshake. An error may be recorded but cannot cancel the in-flight command.

Cycle-exact contract: After cmd_valid_o&&!cmd_ready_i, cmd_valid_o and cmd_o remain stable on all following stalled cycles regardless of status_error_i.

Verification checklist (the implementation is checked beyond examples):
- status_error_i never drops an unaccepted command.
- Payload is immutable while valid is stalled.
- Valid clears only after handshake or reset.
