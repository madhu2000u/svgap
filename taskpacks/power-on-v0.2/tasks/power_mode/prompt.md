Write only this synthesizable SystemVerilog module:

```systemverilog
module power_mode(input logic clk, input logic rst_n, input logic load, input logic mode_in, input logic data_in, output logic data_out);
```

All operational state must reset to zero when active-low `rst_n` is asserted.
Reset assertion may be asynchronous. On a rising edge with `load` high, `mode`
captures `mode_in`. `data_out` equals `data_in` when `mode` is one and equals
zero otherwise. State holds when `load` is low. Do not use `initial` blocks.
