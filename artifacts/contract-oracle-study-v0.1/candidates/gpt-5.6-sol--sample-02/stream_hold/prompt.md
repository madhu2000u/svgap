Create a synthesizable SystemVerilog module with exactly this interface:

```systemverilog
module stream_hold(
    input  logic       clk,
    input  logic       rst_n,
    input  logic       s_valid,
    input  logic [7:0] s_data,
    output logic       s_ready,
    output logic       m_valid,
    output logic [7:0] m_data,
    input  logic       m_ready
);
```

Implement a one-entry ready/valid elastic buffer. A transfer occurs only when
`valid && ready`. Once `m_valid` is asserted, both `m_valid` and `m_data` must
remain stable for every cycle of downstream backpressure (`m_ready == 0`) and
may change only after acceptance. Reset is synchronous active-low and empties
the buffer. Use portable synthesizable RTL and no vendor primitives.

Return only the module, without markdown or explanation.
