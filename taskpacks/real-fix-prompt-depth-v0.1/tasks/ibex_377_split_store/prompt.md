You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module split_store(
    input  logic clk,
    input  logic rst_n,
    input  logic start_i,
    input  logic first_done_i,
    input  logic first_error_i,
    input  logic second_done_i,
    output logic second_req_o,
    output logic complete_o,
    output logic fault_o
);
```

Issue-style context: A misaligned store split into two requests could report the first-half error before the second half had completed.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Always issue and finish the second half after the first response. Latch any first-half error and report completion/fault only with second_done_i.

Cycle-exact contract: After first_done_i, assert second_req_o. Until second_done_i, complete_o and fault_o remain low. At second_done_i, complete_o pulses and fault_o equals the accumulated error.
