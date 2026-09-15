# SV-Gap v0.3.0-alpha.14

This release adds an expanded contract-oracle generation study and the
statistical and replay machinery that supports it. The reference oracles remain
controlled research instruments, and every number below is a bounded,
taskpack-conditional result rather than a production defect rate.

## Expanded contract-oracle generation study v0.1

SV-Gap generated 48 fresh, unrepaired RTL candidates across eight task
clusters, three exact model configurations, and two calls per model-task cell.
The tasks exercise ready/valid persistence, bounded response, one-cycle pulse
width, and synthesized-reference equivalence. Each candidate ran through an
Icarus functional smoke test, one contributing specialized oracle, and
contextual Verilator lint.

Of the 48 candidates, 41 passed their functional harness and 40 produced a
determinate specialized-oracle result. The configured oracles changed the
outcome for 11 of those 40 functionally accepted candidates. This is a
taskpack-conditional automated detection fraction on these eight tasks and 48
outputs. It is not an estimate of defect prevalence in generated RTL, a model
ranking, or a signoff result. The synthesized-reference equivalence stratum is
a bounded null result: all 12 of its candidates passed both the finite
functional harness and the synthesized-reference miter, which shows no detected
divergence on these two tasks rather than general safety under synthesis
semantics.

The protocol and temporal findings are directly inspectable counterexamples,
each carrying a stable finding ID and a replayable report.

## Frozen replay artifact and verifier

The study ships as a frozen, candidate-level replay artifact under
`artifacts/contract-oracle-study-v0.1/`, with the taskpack freeze hash, exact
manifests, properties and references, per-candidate reports, and content
hashes. A deterministic verifier reconstructs and checks the artifact so a
reader can confirm the bundle independently. The underlying
`contract-oracles-v0.1` taskpack is published for reruns.

## Clustered sensitivity analysis and figures

The reset and expanded-contract studies now report whole-task clustered
sensitivity intervals from a 100,000-replicate bootstrap that resamples over
whole tasks rather than individual candidates, so the intervals respect the
dependence between candidates drawn from the same task. The paper figures are
generated from source so they track the underlying reports.

## Prompt-depth study and additional taskpacks

A real-fix prompt-depth study taskpack and runner are included for measuring
how added prompt guidance changes contract outcomes, together with the
`power-on-v0.2` taskpack.

Install or upgrade with `pip install --upgrade svgap`. The optional independent
Naja backend remains available with `pip install "svgap[naja]"`.

## Verified release artifacts

- GitHub: [`v0.3.0-alpha.14`](https://github.com/shsridhar-beep/svgap/releases/tag/v0.3.0-alpha.14)
- PyPI: [`svgap==0.3.0a14`](https://pypi.org/project/svgap/0.3.0a14/)
