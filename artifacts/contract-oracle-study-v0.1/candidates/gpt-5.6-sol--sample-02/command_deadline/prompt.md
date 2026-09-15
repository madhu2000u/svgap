Create a synthesizable SystemVerilog module with exactly this interface:

```systemverilog
module command_deadline(
    input  logic clk,
    input  logic rst_n,
    input  logic start,
    output logic done
);
```

On a rising edge that samples `start` while idle, accept one command. Ignore
new starts while it is pending. Assert `done` for exactly one clock cycle no
later than the third rising edge after acceptance, then return idle. Reset is
synchronous active-low and clears all state. Use portable synthesizable RTL.

Return only the module.
