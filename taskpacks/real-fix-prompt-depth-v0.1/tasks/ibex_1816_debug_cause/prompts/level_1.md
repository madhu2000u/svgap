You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module debug_cause(
    input  logic clk,
    input  logic rst_n,
    input  logic enter_debug_i,
    input  logic debug_req_i,
    input  logic save_cause_i,
    output logic cause_haltreq_o
);
```

Issue-style context: A debug halt request could disappear before a later CSR-save cycle, causing the saved entry cause to describe the wrong event.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Capture the halt-request cause when debug entry is decided and use that captured cause when save_cause_i arrives later.
