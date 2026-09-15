Write only this synthesizable SystemVerilog module:

```systemverilog
module power_hold(input logic clk, input logic rst_n, input logic en, input logic d, output logic q);
```

All operational state must reset to zero when active-low `rst_n` is asserted.
Reset assertion may be asynchronous. On a rising clock edge with `en` high, the module captures `d` and `q` reflects the captured bit; state holds when `en` is low. Do not use `initial` blocks.
