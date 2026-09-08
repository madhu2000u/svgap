# Prompt-depth contract-closure study v0.1

This study asks how much of an RTL contract must be made explicit before each
recorded model configuration closes it. It is deliberately not a leaderboard.
The primary result is a per-task ordinal profile: issue symptom, explicit
behavior, cycle-exact contract, verification checklist, or right-censored.

The full task source is the 24-task `real-fix-prompt-depth-v0.1` taskpack. The
prospective core selects two tasks per category without looking at model output.
The pilot selects one task per category to validate the nine-configuration
matrix and the end-to-end repair workflow before spending on the core.

All Codex configurations use medium reasoning effort so family differences are
not confounded with an effort change. The two local open-weight configurations
use temperature zero and a recorded seed. One call per cell is descriptive and
does not estimate stochastic model reliability.

Run the pilot with:

```bash
.venv/bin/python scripts/run_prompt_depth_study.py \
  --tasks ibex_332_fetch_request ibex_1816_debug_cause cva6_3107_iti_valid \
  --levels 0 1 2 3 --workers 3 --repair
```

Run the six-task core only after the pilot artifacts and model access are
complete. Repairs use the earliest functional-pass/oracle-fail candidate for
each model-task and disclose only the public rule ID and finding message. Final
verification is performed in a fresh candidate directory with the hidden
property/reference unchanged.
