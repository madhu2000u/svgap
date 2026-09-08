# Real-fix prompt-depth taskpack v0.1

This pack contains 24 standalone SystemVerilog reductions derived from 24
historical fail-to-pass records in HWE-Bench: eight protocol, eight temporal,
and eight synthesis/equivalence-semantic tasks. The reductions preserve a bug
mechanism and external contract, not the complete upstream repository or test.
Every task records its PR URL, base SHA, fix-patch digest, original HWE-Bench
problem statement, and an explicit reduction limitation in `source.json`.

Each task has four cumulative model-visible prompt levels. The interface,
functional smoke test, hidden contributing oracle, and reference are identical
at every level. The intended outcome is the minimum observed prompt depth that
closes the contract, not a scalar model leaderboard.

The finite Icarus smoke test is deliberately incomplete. A separate bounded
Yosys property or post-Yosys reference-equivalence miter is the contributing
oracle. Verilator lint is noncontributing context. Both safe and unsafe reference
implementations must pass the smoke test; only the hidden oracle separates them.
