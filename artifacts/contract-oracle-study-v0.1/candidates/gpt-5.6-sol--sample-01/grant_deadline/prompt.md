Write a synthesizable SystemVerilog module with exactly this interface:

```systemverilog
module grant_deadline(
    input  logic clk,
    input  logic rst_n,
    input  logic request,
    output logic grant
);
```

When idle, accept a request on a rising edge. Ignore additional requests while
one is pending. Produce a one-cycle `grant` pulse no later than the second
rising edge after acceptance, then return idle. Reset is synchronous active-low
and clears all state. Use portable synthesizable RTL.

Return only the module.
