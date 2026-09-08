You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module csr_mask(
    input  logic [15:0] old_mstatus_i,
    input  logic [15:0] write_mstatus_i,
    input  logic [15:0] write_satp_ppn_i,
    output logic [15:0] new_mstatus_o,
    output logic [15:0] new_satp_ppn_o
);
```

Issue-style context: CSR writes could modify a read-only status field and preserve page-number bits above the implementation's physical-address width.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Preserve old_mstatus_i[5:4] across writes and accept all other mstatus bits. Keep only satp_ppn_i[11:0], forcing its upper four output bits to zero.
