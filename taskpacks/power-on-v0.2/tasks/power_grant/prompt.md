Write only this synthesizable SystemVerilog module:

```systemverilog
module power_grant(input logic clk, input logic rst_n, input logic req, input logic done, output logic grant);
```

All operational state must reset to zero when active-low `rst_n` is asserted.
Reset assertion may be asynchronous. On a rising clock edge, `req` asserts `grant` and `done` deasserts it to zero, with `done` taking priority; state holds otherwise. Do not use `initial` blocks.
