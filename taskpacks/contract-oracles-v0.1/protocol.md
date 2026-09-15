# Contract-oracle study protocol

## Question

Among fresh model generations that pass each task's finite smoke test, does a
property-appropriate protocol, temporal, or synthesized-equivalence oracle find
violations of an explicit requirement that the smoke test does not identify?

## Frozen design

- Eight task clusters: two per contributing rule.
- Fresh single-turn calls with tools disabled and no repair.
- Two calls per model-task cell in the initial multi-model run.
- Candidate-level functional and oracle outcomes, grouped by task.
- Task-resampling intervals reported only as finite-task sensitivity analyses.

The primary count is functional pass plus contributing-oracle fail. Compile
errors, functional failures, unknowns, and tool errors remain separate. Model
results are descriptive; the study is not powered for a leaderboard. Ordinary
lint is contextual and cannot contribute to gap membership.

## Calibration

Before generation, both references for every task must pass the same functional
test. The safe reference must pass its contributing oracle and the unsafe
reference must fail with the task's declared rule. Any failing calibration
blocks model-outcome interpretation.
