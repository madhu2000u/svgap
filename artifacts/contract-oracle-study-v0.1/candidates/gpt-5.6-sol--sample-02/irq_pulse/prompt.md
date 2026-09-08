Create a synthesizable SystemVerilog module with exactly this interface:

```systemverilog
module irq_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic trigger,
    output logic irq
);
```

For each isolated one-cycle `trigger`, assert `irq` for exactly one clock cycle.
Never stretch the interrupt into a second cycle. Reset is synchronous
active-low and clears `irq`. Use portable synthesizable RTL.

Return only the module.
