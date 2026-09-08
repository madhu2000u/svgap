# Contract-oracle multi-model study v0.1

This artifact freezes 48 unrepaired candidates: eight task clusters, three
model configurations, and two fresh calls per model-task cell. The tasks cover
ready/valid persistence, bounded response, exactly one-cycle pulses, and
synthesized-reference equivalence. Each bundle contains the prompt, normalized
RTL, finite Icarus smoke test, property/reference source, multi-oracle report,
generation metadata, selected formal evidence, and content hashes.

Of 48 candidates, 41 pass the
functional smoke tests. 40 of those
receive a determinate contributing-oracle result, and 11
are gap members. The descriptive fraction is
`11/40 =
27.5%`. Resampling all candidates within each task as a
cluster gives a 95% percentile interval of `7.3%` to
`48.8%`. Because the eight tasks were hand-authored, this is a
finite-task sensitivity interval, not a population-prevalence interval.

All 11 gap members have Verilator lint status `pass`. One has an unrelated
unused-signal warning; none has a lint diagnostic identifying the specialized
protocol or temporal violation. All 12 synthesized-equivalence candidates pass
the equivalence oracle, so that stratum is a bounded null result.

The excluded parallel interface pilot is not part of this artifact. It loaded
two local models concurrently, causing HTTP 500 generation failures, and was
stopped before the sequential primary run. No pilot candidate enters the 48
reported candidates.

Replay a candidate with:

```bash
svgap check artifacts/contract-oracle-study-v0.1/candidates/<run>/<task>/manifest.toml
```

Verify hashes, outcome indices, portability, and clustered analysis with:

```bash
.venv/bin/python scripts/verify_contract_oracle_artifacts.py
```
