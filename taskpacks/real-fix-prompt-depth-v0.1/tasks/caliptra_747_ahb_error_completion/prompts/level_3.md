You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module ahb_error_completion(
    input  logic clk,
    input  logic rst_n,
    input  logic transfer_i,
    input  logic done_i,
    input  logic error_i,
    output logic dv_o
);
```

Issue-style context: An internal AHB request-valid signal remained asserted for an extra cycle after an outstanding request completed with an error.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Assert dv_o for an accepted transfer and clear it as soon as either a normal or error completion is sampled.

Cycle-exact contract: After a rising edge that samples dv_o&&(done_i||error_i), dv_o is low in the following cycle and remains low until a new transfer_i.

Verification checklist (the implementation is checked beyond examples):
- Error completion and normal completion retire the request identically.
- No one-cycle tail is allowed after completion.
- Reset clears dv_o.
