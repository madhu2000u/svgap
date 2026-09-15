You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module delayed_misaligned(
    input  logic clk,
    input  logic rst_n,
    input  logic request_i,
    input  logic misaligned_i,
    output logic response_o,
    output logic misaligned_o
);
```

Issue-style context: A one-cycle-delayed MMU response could use the misalignment state from the wrong request cycle or leak it into an idle cycle.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Pipeline request validity and its misaligned flag together so the response exception belongs to the originating access.

Cycle-exact contract: response_o in cycle N+1 equals request_i from cycle N. When response_o is high, misaligned_o equals misaligned_i captured with that request; when response_o is low, misaligned_o is low.
