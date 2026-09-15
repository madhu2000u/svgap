Write only this synthesizable SystemVerilog module:

```systemverilog
module power_gate(input logic clk, input logic rst_n, input logic open_gate, input logic close_gate, input logic din, output logic dout);
```

All operational state must reset to zero when active-low `rst_n` is asserted.
Reset assertion may be asynchronous. On a rising clock edge, `open_gate` opens the gate and `close_gate` closes it, with `close_gate` taking priority; when the gate is open `dout` equals `din`, and when closed `dout` is zero. Do not use `initial` blocks.
