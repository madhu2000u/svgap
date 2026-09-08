from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import random
from typing import Any, Iterable

from svgap.validation import (
    contributing_oracle_status,
    oracle_results,
    validate_report_payload,
)


def analyze_reports(
    report_paths: Iterable[Path],
    *,
    bootstrap_replicates: int = 100_000,
    bootstrap_seed: int = 20_260_824,
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for path in sorted({item.resolve() for item in report_paths}):
        report = validate_report_payload(json.loads(path.read_text(encoding="utf-8")))
        contributing = [
            item for item in oracle_results(report) if item["contributes_to_gap"]
        ]
        lint = [item for item in oracle_results(report) if item["oracle_class"] == "lint"]
        run_id = path.parent.parent.name
        records.append(
            {
                "path": path,
                "task": report["candidate_id"],
                "run_id": run_id,
                "model": run_id.split("--sample-", 1)[0],
                "functional": report["functional"]["status"],
                "contributing_status": contributing_oracle_status(report),
                "gap_member": bool(report["gap_member"]),
                "oracle_classes": sorted(
                    {item["oracle_class"] for item in contributing}
                ),
                "rules": sorted(
                    {
                        rule
                        for item in contributing
                        for rule in item.get("coverage", {}).get("rules", [])
                    }
                ),
                "finding_rules": sorted(
                    {
                        finding["rule_id"]
                        for item in contributing
                        for finding in item.get("findings", [])
                    }
                ),
                "lint_status": combined_status(item["status"] for item in lint),
                "lint_findings": sum(len(item.get("findings", [])) for item in lint),
            }
        )
    if not records:
        raise ValueError("no reports were supplied")

    overall = summarize_records(records)
    overall["task_cluster_bootstrap"] = task_cluster_bootstrap(
        records,
        replicates=bootstrap_replicates,
        seed=bootstrap_seed,
    )
    by_model: dict[str, Any] = {}
    for model in sorted({record["model"] for record in records}):
        selected = [record for record in records if record["model"] == model]
        item = summarize_records(selected)
        item["task_cluster_bootstrap"] = task_cluster_bootstrap(
            selected,
            replicates=bootstrap_replicates,
            seed=bootstrap_seed,
        )
        by_model[model] = item

    gap_records = [record for record in records if record["gap_member"]]
    lint_on_gaps = Counter(record["lint_status"] for record in gap_records)
    by_task = {
        task: summarize_records([record for record in records if record["task"] == task])
        for task in sorted({record["task"] for record in records})
    }
    by_class = {
        oracle_class: summarize_records(
            [
                record
                for record in records
                if oracle_class in record["oracle_classes"]
            ]
        )
        for oracle_class in sorted(
            {item for record in records for item in record["oracle_classes"]}
        )
    }
    return {
        "schema_version": "1.0",
        "analysis_unit": "candidate report",
        "cluster_unit": "task",
        "overall": overall,
        "by_model": by_model,
        "by_task": by_task,
        "by_oracle_class": by_class,
        "lint_on_gap_members": {
            "gap_members": len(gap_records),
            "statuses": dict(sorted(lint_on_gaps.items())),
            "gap_members_with_any_lint_finding": sum(
                record["lint_findings"] > 0 for record in gap_records
            ),
        },
        "interpretation": {
            "interval": (
                "nonparametric task-cluster bootstrap percentile interval; "
                "a finite-task sensitivity analysis, not a population-prevalence interval"
            ),
            "gap_denominator": (
                "functional passes with contributing oracle status pass or fail; "
                "unknown and tool_error are excluded"
            ),
            "model_comparison": "descriptive only; not powered as a model ranking",
        },
    }


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    functional = Counter(record["functional"] for record in records)
    contributing = Counter(record["contributing_status"] for record in records)
    eligible = [
        record
        for record in records
        if record["functional"] == "pass"
        and record["contributing_status"] in ("pass", "fail")
    ]
    gaps = sum(record["gap_member"] for record in eligible)
    return {
        "reports": len(records),
        "tasks": len({record["task"] for record in records}),
        "functional_statuses": dict(sorted(functional.items())),
        "contributing_oracle_statuses": dict(sorted(contributing.items())),
        "determinate_functional_passes": len(eligible),
        "gap_members": gaps,
        "gap_fraction": gaps / len(eligible) if eligible else None,
    }


def task_cluster_bootstrap(
    records: list[dict[str, Any]], *, replicates: int, seed: int
) -> dict[str, Any] | None:
    if replicates < 1:
        raise ValueError("bootstrap replicates must be positive")
    clusters: dict[str, tuple[int, int]] = {}
    for task in sorted({record["task"] for record in records}):
        eligible = [
            record
            for record in records
            if record["task"] == task
            and record["functional"] == "pass"
            and record["contributing_status"] in ("pass", "fail")
        ]
        clusters[task] = (
            sum(record["gap_member"] for record in eligible),
            len(eligible),
        )
    if len(clusters) < 2 or not sum(value[1] for value in clusters.values()):
        return None
    values = list(clusters.values())
    rng = random.Random(seed)
    samples: list[float] = []
    skipped = 0
    for _ in range(replicates):
        chosen = [values[rng.randrange(len(values))] for _ in values]
        denominator = sum(item[1] for item in chosen)
        if not denominator:
            skipped += 1
            continue
        samples.append(sum(item[0] for item in chosen) / denominator)
    samples.sort()
    return {
        "method": "nonparametric task-cluster bootstrap, percentile interval",
        "estimand": "candidate-weighted gap fraction after resampling whole tasks",
        "cluster_count": len(clusters),
        "replicates_requested": replicates,
        "replicates_used": len(samples),
        "zero_denominator_replicates": skipped,
        "seed": seed,
        "estimate": sum(value[0] for value in values) / sum(
            value[1] for value in values
        ),
        "confidence_level": 0.95,
        "lower": quantile(samples, 0.025),
        "upper": quantile(samples, 0.975),
        "clusters": {
            task: {"gap_members": value[0], "determinate_functional_passes": value[1]}
            for task, value in clusters.items()
        },
    }


def quantile(sorted_values: list[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("cannot compute a quantile of an empty sample")
    if not 0 <= probability <= 1:
        raise ValueError("quantile probability must be in [0, 1]")
    position = (len(sorted_values) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = position - lower
    return sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction


def combined_status(statuses: Iterable[str]) -> str:
    values = list(statuses)
    for status in ("tool_error", "fail", "unknown", "compile_error", "pass", "not_run"):
        if status in values:
            return status
    return "not_run"
