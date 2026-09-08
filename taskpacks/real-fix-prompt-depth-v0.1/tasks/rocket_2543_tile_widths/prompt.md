You are implementing a standalone SystemVerilog reduction derived from a real historical RTL fix. Implement exactly this interface:

```systemverilog
module tile_widths(
    input  logic [15:0] hart_id_i,
    input  logic [47:0] reset_vector_i,
    output logic [15:0] tile_hart_id_o,
    output logic [47:0] tile_reset_vector_o
);
```

Issue-style context: Tile HartID and reset-vector ports could be narrower than the configured values in heterogeneous elaborations.

Use portable synthesizable SystemVerilog and no vendor primitives. Return only the complete module, without markdown or explanation.

Required externally observable behavior: Preserve the full 16-bit HartID and full 48-bit reset vector on the corresponding Tile-facing outputs.

Cycle-exact contract: Combinationally, tile_hart_id_o===hart_id_i and tile_reset_vector_o===reset_vector_i for all bits and all values.
