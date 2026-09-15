Write only this synthesizable SystemVerilog module:

```systemverilog
module power_valid(input logic clk, input logic rst_n, input logic load, input logic valid_in, input logic payload_in, output logic payload_out);
```

All operational state must reset to zero when active-low `rst_n` is asserted.
Reset assertion may be asynchronous. On a rising edge with `load` high,
`valid` and `payload` capture `valid_in` and `payload_in`. `payload_out` equals
`payload` when `valid` is one and equals zero otherwise. State holds when
`load` is low. Do not use `initial` blocks.
