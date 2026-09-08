# Prompt-depth contract-closure protocol

## Treatments

- `level_0`: issue-style symptom and interface only.
- `level_1`: adds an explicit externally observable behavior.
- `level_2`: adds cycle-exact semantics.
- `level_3`: adds a verification-oriented checklist without oracle source code.

Levels are cumulative. Calls are fresh and independent: a model does not see
its output or result at another level. All non-prompt task inputs are matched.

## Outcomes

For each model-configuration/task cell report functional pass, specialized
oracle pass, first observed contract-closing depth, non-monotone level outcomes,
and whether concise oracle feedback repairs a functional-pass/oracle-fail
candidate. Treat no observed closure through level 3 as right-censored. Do not
rank models by a single aggregate pass rate.

## Repair and final verification

The repair call receives the original visible prompt, candidate RTL, and only
the public finding ID/message (never the hidden property or reference). The
returned module is materialized in a fresh directory and re-run through the
same functional, contributing-oracle, and noncontributing-lint profile. Report
repair transitions rather than silently replacing the initial outcome.

## Unit of analysis and limits

The task cluster, not a prompt level or generated candidate, is the resampling
unit. One generation per cell measures these recorded configurations, not a
stochastic population of model behavior. These reauthored reductions support
mechanism-level analysis; HWE-Bench remains the source for full-repository agent
repair claims.
