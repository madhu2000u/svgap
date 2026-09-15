You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module icache_response(
    input  logic        clk,
    input  logic        rst_n,
    input  logic        available_i,
    input  logic [31:0] data_i,
    input  logic        ready_i,
    output logic        valid_o,
    output logic [31:0] data_o
);
```

Issue-style context: A completed instruction response could be withheld while the consumer was not ready, coupling response availability to acceptance.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Buffer each available response. Assert valid as soon as it is buffered, independent of ready, and retain the response until accepted.

Cycle-exact contract: At a rising edge with available_i=1, capture data_i. From the following cycle through the first cycle with valid_o&&ready_i, valid_o is 1 and data_o is unchanged. ready_i controls consumption only.

Verification checklist (the implementation is checked beyond examples):
- A response arriving while ready_i=0 is still advertised on valid_o.
- valid_o and data_o are stable throughout backpressure.
- Synchronous active-low reset clears valid_o.
