Write a synthesizable SystemVerilog module with exactly this interface:

```systemverilog
module completion_pulse(
    input  logic clk,
    input  logic rst_n,
    input  logic event_done,
    output logic completed
);
```

Convert each isolated one-cycle `event_done` into an exactly one-cycle
`completed` pulse. `completed` must be low on the following cycle even if no
other event occurs. Reset is synchronous active-low and clears the output. Use
portable synthesizable RTL.

Return only the module.
