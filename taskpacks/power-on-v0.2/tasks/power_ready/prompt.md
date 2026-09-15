Write only this synthesizable SystemVerilog module:

```systemverilog
module power_ready(input logic clk, input logic rst_n, input logic start, input logic clear, output logic ready);
```

All operational state must reset to zero when active-low `rst_n` is asserted.
Reset assertion may be asynchronous. On a rising clock edge, `start` sets `ready` high and `clear` clears it to zero, with `clear` taking priority; state holds otherwise. Do not use `initial` blocks.
