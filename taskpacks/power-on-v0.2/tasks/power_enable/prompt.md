Write only this synthesizable SystemVerilog module:

```systemverilog
module power_enable(input logic clk, input logic rst_n, input logic load, input logic enable_in, output logic active);
```

All operational state must reset to zero when active-low `rst_n` is asserted.
Reset assertion may be asynchronous. On a rising edge with `load` high,
`enabled` captures `enable_in`. `active` equals `enabled`. State holds when
`load` is low. Do not use `initial` blocks.
