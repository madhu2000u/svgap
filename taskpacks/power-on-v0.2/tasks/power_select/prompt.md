Write only this synthesizable SystemVerilog module:

```systemverilog
module power_select(input logic clk, input logic rst_n, input logic load, input logic [1:0] select_in, input logic [3:0] data_in, output logic data_out);
```

All operational state must reset to zero when active-low `rst_n` is asserted.
Reset assertion may be asynchronous. On a rising edge with `load` high,
`select` captures `select_in`. `data_out` selects the correspondingly indexed
bit of `data_in`. State holds when `load` is low. Do not use `initial` blocks.
