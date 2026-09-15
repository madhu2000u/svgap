# When offline success cannot identify production validity

## Compact research artifact

AI research teams commonly evaluate generated artifacts with executable offline
oracles: compile the artifact, run a test suite, compare outputs, and report a
pass rate. Production teams inherit a different obligation. They must determine
whether the implementation satisfies deployment properties that may be absent
from the functional semantics and absent from the benchmark metadata.

SV-Gap makes that handoff failure explicit for generated RTL. Clock-domain and
reset-domain safety are the first case study because standard RTL simulation
does not reproduce analog metastability or recovery/removal timing. The current
contract also carries power-on/X behavior, protocol persistence, temporal
response and pulse properties, and synthesized-reference equivalence.

## Central result

```text
                         OFFLINE FUNCTIONAL ORACLE
                      same observation: both PASS
                         /                 \
                        /                   \
       reference implementation       hazardous implementation
                        \                   /
                         \                 /
                 DECLARED PRODUCTION INTENT +
                      STRUCTURAL ORACLE
                       PASS          FAIL
```

Twenty-two controlled witness pairs instantiate this construction across 21
stable finding IDs. Both members of each pair pass the supplied functional
simulation while the configured production oracle separates the safe and
unsafe cases. Seventeen pairs exercise structural classes; five exercise
protocol/temporal or reference-equivalence semantics. These deliberately
controlled pairs validate the measurement harness; they are not a defect-rate
estimate.

## Why this is a trust problem

The production team cannot infer the missing property from a functional pass.
In many cases it cannot even run the additional evaluation because the research
artifact does not state the clock groups, reset semantics, crossing protocol, or
other intent that gives the property meaning. The resulting distrust is not
necessarily resistance to AI or a demand for more benchmark examples. It is a
traceable mismatch between what the offline result establishes and what the
production decision requires.

SV-Gap represents that mismatch as a layered record:

```text
functional result + production intent + structural result + evidence
```

Each oracle may return `pass`, `fail`, `unknown`, or `tool_error`. Missing
intent and analyzer limitations therefore remain visible instead of being
converted into apparent success. Ordinary lint remains a separate contextual
class and cannot silently substitute for a configured specialized oracle.

## Public benchmark inventory

The current automated inventory covers 508 tasks from VerilogEval, RTLLM, and
CVDP. It detects 12 tasks with multiple clock-like ports, 11 with sufficient
intent for the reference audit, and no recognizable native CDC/RDC scoring
artifact. These are heuristic inventory counts, not a validated census. Their
role in the existential argument is diagnostic: current task formats frequently
do not expose the metadata needed for this production question.

A separate power-on inventory over the same 508 tasks detects 373 sequential
tasks and 253 with a reset-like input. Only 28 state comprehensive state-reset
intent, and no harness contains recognizable scoring
that perturbs unknown internal initial state. This second detector is also a
descriptive heuristic, not a validated census.

A third audit finds at least 98 tasks with an explicit temporal, persistence,
progress, or protocol contract but no recognizable native property/formal
score. It also finds 16 explicit-equivalence tasks with original RTL and Yosys
synthesis but no recognizable equivalence or post-synthesis behavioral
comparison. These are conservative missing-evidence lower bounds, not counts of
incorrect generated designs.

## Generated-RTL demonstration

A frozen reset-release taskpack generated 72 outputs across eight tasks and
three model configurations. Fifty-seven passed the supplied Icarus testbenches.
The reference oracle identified at least 14 of those accepted outputs with a raw
asynchronous-reset connection to operational state despite a synchronized-
release requirement. The 72 calls contain 69 unique normalized RTL texts; the
three duplicate pairs are structural passes and do not change the 14 detected
cases.

The result demonstrates recurrence within the taskpack and supplies public
artifacts for inspection. It does not estimate the frequency of the pattern in
all generated RTL. A blinded synthetic panel reproduced the case-level split,
but synthetic agreement is robustness evidence rather than human signoff.

A second frozen study generated 48 fresh, unrepaired outputs over eight
protocol, temporal, and synthesized-equivalence tasks. Forty-one pass the
finite functional harness; 40 receive a determinate contributing-oracle result;
and 11 fail the configured protocol or temporal property. All 11 retain
Verilator lint status `pass`. Both equivalence tasks produce bounded null
results (`0/12`). A whole-task bootstrap gives a 7.3%–48.8% finite-task
sensitivity interval around `11/40`; it is not a population-prevalence
interval.

## Contribution

The contribution is an executable evaluation contract for making production
trust failures legible:

1. attach explicit production intent to an evaluated artifact;
2. preserve the original functional result rather than replacing it;
3. apply independently versioned production-oriented oracles;
4. distinguish findings, missing information, and tool failures;
5. retain source-level evidence and provenance; and
6. allow alternative backends and adjudications to disagree visibly.

This changes the research-to-production conversation from “the benchmark says
it works” versus “production does not trust it” to a concrete account of which
property was measured, which was not, what information is missing, and what
evidence would resolve the disagreement.

## Interpretation boundary

SV-Gap is not silicon signoff and its reference rules are intentionally
narrow. The framework is useful even when a team substitutes a commercial or
independent open checker: the durable contribution is the intent and evidence
contract, not the completeness of one backend.

## Reproduction map

- Controlled witnesses: `examples/`
- Public benchmark inventory: `reports/audits/`
- Reset taskpack: `taskpacks/reset-replication-v0.1/`
- Generated candidates: `artifacts/reset-replication-v0.1/`
- Expanded contract taskpack: `taskpacks/contract-oracles-v0.1/`
- Expanded candidate artifact: `artifacts/contract-oracle-study-v0.1/`
- Ordinary RTL lint baseline: `docs/rdc-lint-baseline-result.md` and
  `reports/rdc-lint-baseline-v0.1/`
- Results: `docs/reset-replication-result.md` and
  `docs/contract-oracle-study-result.md`
- Limitations: `docs/limitations.md`
- Machine-readable contracts: `schemas/`
