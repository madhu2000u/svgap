You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module fetch_request(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        start_i,
    input  logic [31:0] start_addr_i,
    input  logic        redirect_i,
    input  logic [31:0] redirect_addr_i,
    input  logic        gnt_i,
    output logic        req_o,
    output logic [31:0] addr_o
);
```

Issue-style context: A branch redirect could replace the address of an instruction request that had not yet received a grant.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Once a fetch request is issued, preserve its request and address until the request/grant handshake completes; queue no redirect into that beat.
