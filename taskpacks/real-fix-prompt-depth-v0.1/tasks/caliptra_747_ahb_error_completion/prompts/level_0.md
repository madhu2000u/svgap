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
