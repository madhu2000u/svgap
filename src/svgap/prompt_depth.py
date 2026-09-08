"""Analysis helpers for matched prompt-depth and oracle-repair studies."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable


PROMPT_LEVELS = ("level_0", "level_1", "level_2", "level_3")
LEVEL_LABELS = {
    "level_0": "issue symptom",
    "level_1": "explicit behavior",
    "level_2": "cycle-exact contract",
    "level_3": "verification checklist",
}


def contributing_status(report: dict[str, Any]) -> str:
    statuses = [
        oracle["status"]
        for oracle in report.get("oracle_results", [])
        if oracle.get("contributes_to_gap")
    ]
    return combined_status(statuses)


def lint_status(report: dict[str, Any]) -> str:
    statuses = [
        oracle["status"]
        for oracle in report.get("oracle_results", [])
        if oracle.get("oracle_class") == "lint"
    ]
    return combined_status(statuses)


def combined_status(statuses: Iterable[str]) -> str:
    values = list(statuses)
    for status in ("tool_error", "unknown", "fail", "pass", "not_run"):
        if status in values:
            return status
    return "not_configured"


def report_outcome(report: dict[str, Any]) -> dict[str, Any]:
    functional = report["functional"]["status"]
    oracle = contributing_status(report)
    return {
        "functional_status": functional,
        "contributing_oracle_status": oracle,
        "lint_status": lint_status(report),
        "gap_member": functional == "pass" and oracle == "fail",
        "contract_closed": functional == "pass" and oracle == "pass",
        "finding_ids": sorted(
            {
                finding["rule_id"]
                for result in report.get("oracle_results", [])
                if result.get("contributes_to_gap")
                for finding in result.get("findings", [])
            }
        ),
        "finding_messages": sorted(
            {
                finding["message"]
                for result in report.get("oracle_results", [])
                if result.get("contributes_to_gap")
                for finding in result.get("findings", [])
            }
        ),
    }


def repair_prompt(
    original_prompt: str, candidate: str, report: dict[str, Any]
) -> str:
    outcome = report_outcome(report)
    findings = "\n".join(
        f"- {rule}: {message}"
        for rule, message in zip(
            outcome["finding_ids"], outcome["finding_messages"], strict=False
        )
    )
    if not findings:
        findings = "- The specialized contract oracle failed without a public finding message."
    return f"""{original_prompt.rstrip()}

The candidate below passed the finite functional smoke test but failed a
specialized contract oracle:

{findings}

Repair the candidate so it preserves the requested behavior and closes the
reported contract. Do not rely on the smoke-test examples alone. Return only
the complete corrected module, without markdown or explanation.

Candidate to repair:
```systemverilog
{candidate.rstrip()}
```
"""


def summarize_prompt_depth(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(records)
    initial = [row for row in rows if row.get("phase") == "initial"]
    repairs = [row for row in rows if row.get("phase") == "repair"]
    configurations = sorted({str(row["configuration_label"]) for row in initial})
    profiles = {
        configuration: _configuration_profile(
            configuration,
            [row for row in initial if row["configuration_label"] == configuration],
            [row for row in repairs if row["configuration_label"] == configuration],
        )
        for configuration in configurations
    }
    return {
        "schema_version": "1.0",
        "estimand": (
            "first observed cumulative prompt level achieving functional pass plus "
            "contributing-oracle pass for each recorded model-configuration/task cell"
        ),
        "not_a_leaderboard": True,
        "prompt_levels": [
            {"id": level, "ordinal": index, "label": LEVEL_LABELS[level]}
            for index, level in enumerate(PROMPT_LEVELS)
        ],
        "records": len(rows),
        "initial_records": len(initial),
        "repair_records": len(repairs),
        "configurations": profiles,
        "cross_configuration": _cross_configuration(initial),
        "interpretation_limits": [
            "One call per cell describes recorded configurations, not stochastic model populations.",
            "First observed closure is not assumed monotone; reversals are reported explicitly.",
            "Tasks are standalone real-fix-derived reductions, not full upstream regressions.",
            "A censored cell did not close through level_3; it is not assigned an artificial depth.",
        ],
    }


def _configuration_profile(
    configuration: str,
    initial: list[dict[str, Any]],
    repairs: list[dict[str, Any]],
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in initial:
        grouped[str(row["task_id"])].append(row)
    tasks: list[dict[str, Any]] = []
    depth_distribution: Counter[str] = Counter()
    functional_depth_distribution: Counter[str] = Counter()
    non_monotone = 0
    for task_id, task_rows in sorted(grouped.items()):
        task_rows.sort(key=lambda row: int(row["prompt_ordinal"]))
        closed = [row for row in task_rows if row.get("contract_closed")]
        functional = [row for row in task_rows if row.get("functional_status") == "pass"]
        first_closed = min((int(row["prompt_ordinal"]) for row in closed), default=None)
        first_functional = min(
            (int(row["prompt_ordinal"]) for row in functional), default=None
        )
        key = str(first_closed) if first_closed is not None else "censored"
        functional_key = (
            str(first_functional) if first_functional is not None else "censored"
        )
        depth_distribution[key] += 1
        functional_depth_distribution[functional_key] += 1
        closure_sequence = [bool(row.get("contract_closed")) for row in task_rows]
        reversal = any(
            closure_sequence[index]
            and not any(closure_sequence[index + 1 : index + 2])
            for index in range(len(closure_sequence) - 1)
        )
        non_monotone += int(reversal)
        tasks.append(
            {
                "task_id": task_id,
                "category": task_rows[0].get("category"),
                "first_functional_depth": first_functional,
                "first_contract_closure_depth": first_closed,
                "right_censored": first_closed is None,
                "non_monotone_closure": reversal,
                "levels": {
                    row["prompt_level"]: {
                        "generation_status": row.get("generation_status"),
                        "functional_status": row.get("functional_status"),
                        "oracle_status": row.get("contributing_oracle_status"),
                        "contract_closed": bool(row.get("contract_closed")),
                    }
                    for row in task_rows
                },
            }
        )
    repair_eligible = len(repairs)
    repair_closed = sum(bool(row.get("contract_closed")) for row in repairs)
    by_category: dict[str, Counter[str]] = defaultdict(Counter)
    for task in tasks:
        key = (
            str(task["first_contract_closure_depth"])
            if task["first_contract_closure_depth"] is not None
            else "censored"
        )
        by_category[str(task["category"])][key] += 1
    return {
        "configuration_label": configuration,
        "provider": initial[0].get("provider") if initial else None,
        "requested_model": initial[0].get("requested_model") if initial else None,
        "tasks_observed": len(tasks),
        "depth_distribution": _ordered_depth_counts(depth_distribution),
        "functional_depth_distribution": _ordered_depth_counts(
            functional_depth_distribution
        ),
        "by_category": {
            category: _ordered_depth_counts(counts)
            for category, counts in sorted(by_category.items())
        },
        "non_monotone_tasks": non_monotone,
        "repair": {
            "eligible_gap_candidates_repaired": repair_eligible,
            "contract_closed_after_feedback": repair_closed,
            "still_open_or_indeterminate": repair_eligible - repair_closed,
        },
        "task_profiles": tasks,
    }


def _ordered_depth_counts(values: Counter[str]) -> dict[str, int]:
    return {key: values.get(key, 0) for key in ("0", "1", "2", "3", "censored")}


def _cross_configuration(initial: list[dict[str, Any]]) -> dict[str, Any]:
    by_task_level: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in initial:
        by_task_level[(str(row["task_id"]), str(row["prompt_level"]))].append(row)
    disagreements = []
    for (task_id, level), rows in sorted(by_task_level.items()):
        states = {
            row["configuration_label"]: bool(row.get("contract_closed")) for row in rows
        }
        if len(set(states.values())) > 1:
            disagreements.append(
                {"task_id": task_id, "prompt_level": level, "closure": states}
            )
    return {
        "matched_cells_with_model_disagreement": len(disagreements),
        "disagreements": disagreements,
    }

