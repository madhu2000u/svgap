You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module ptw_address(
    input  logic [34:0] vpn_fragment_i,
    output logic [55:0] pte_addr_o
);
```

Issue-style context: Sv57 plus hypervisor configuration built a page-table address from a fragment narrower than the slice assumed by the implementation.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.
