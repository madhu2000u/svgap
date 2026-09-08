# Contract-oracle generation study v0.1

Eight frozen generation tasks exercise four SV-Gap rules beyond CDC/RDC and
power-on structure: ready/valid persistence (`REF-PROT-001`), bounded response
(`REF-TEMP-001`), one-cycle pulse width (`REF-TEMP-002`), and synthesized
reference equivalence (`REF-EQUIV-001`). Each rule has two task clusters.

Every task has a finite Icarus smoke test plus a distinct contributing formal
property or synthesized-reference oracle. The safe and unsafe references both
pass the same smoke test; the specialized oracle separates them. Verilator lint
is retained as noncontributing context. The design is a prospective local
freeze, not an externally timestamped preregistration or a population sample.
