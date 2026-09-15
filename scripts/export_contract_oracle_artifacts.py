#!/usr/bin/env python3
"""Export the frozen multi-model contract-oracle study as portable evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

from svgap.provenance import canonical_file_set_digest
from svgap.statistics import analyze_reports, combined_status
from svgap.validation import (
    contributing_oracle_status,
    oracle_results,
    validate_report_payload,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports/generated/contract-oracles-v0.1"
TASKS = ROOT / "taskpacks/contract-oracles-v0.1"
DEFAULT_OUTPUT = ROOT / "release_staging/contract-oracle-study-v0.1"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--taskpack", type=Path, default=TASKS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = args.source.resolve()
    taskpack = args.taskpack.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite release staging directory: {output}")
    manifests = sorted(source.glob("*/*/*/manifest.toml"))
    if len(manifests) != 48:
        raise SystemExit(f"expected 48 primary candidates, found {len(manifests)}")
    candidates_root = output / "candidates"
    candidates_root.mkdir(parents=True)
    evaluator_files = sorted((ROOT / "src/svgap").rglob("*.py"))
    evaluator_digest = canonical_file_set_digest(ROOT, evaluator_files)
    index: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []

    for manifest_path in manifests:
        source_dir = manifest_path.parent
        run_id = source_dir.parent.name
        task_id = source_dir.name
        model = run_id.split("--sample-", 1)[0]
        target = candidates_root / run_id / task_id
        target.mkdir(parents=True)
        task_dir = taskpack / "tasks" / task_id
        support_name = (
            "reference.sv" if (task_dir / "reference.sv").is_file() else "properties.sv"
        )
        for source_path, target_name in (
            (source_dir / "design.sv", "design.sv"),
            (task_dir / "prompt.md", "prompt.md"),
            (task_dir / "task.toml", "task.toml"),
            (task_dir / "tb.sv", "tb.sv"),
            (task_dir / support_name, support_name),
        ):
            shutil.copy2(source_path, target / target_name)
        portable_manifest = manifest_path.read_text(encoding="utf-8").replace(
            '"task-testbench.sv"', '"tb.sv"'
        )
        (target / "manifest.toml").write_text(portable_manifest, encoding="utf-8")
        generation = json.loads(
            (source_dir / "generation.json").read_text(encoding="utf-8")
        )
        generation.pop("command", None)
        (target / "generation.json").write_text(
            json.dumps(generation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        completed = subprocess.run(
            [sys.executable, "-m", "svgap", "check", str(target / "manifest.toml")],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        replay_path = target / "report.json"
        if completed.returncode not in (0, 1, 2, 3) or not replay_path.is_file():
            raise SystemExit(f"replay failed for {run_id}/{task_id}: {completed.stderr}")
        source_report = validate_report_payload(
            json.loads((source_dir / "report.json").read_text(encoding="utf-8"))
        )
        replay = validate_report_payload(json.loads(replay_path.read_text(encoding="utf-8")))
        assert_same_outcome(source_report, replay, run_id=run_id, task_id=task_id)
        replay["generated_at"] = source_report["generated_at"]
        replay["manifest"] = "manifest.toml"

        evidence_dir = target / "evidence"
        build_dir = target / "build"
        evidence_files: list[Path] = []
        if build_dir.is_dir():
            for path in sorted(build_dir.iterdir()):
                if path.suffix not in (".log", ".vcd", ".ys"):
                    continue
                evidence_dir.mkdir(exist_ok=True)
                evidence_path = evidence_dir / path.name
                text = portable_text(
                    path.read_text(encoding="utf-8", errors="replace"),
                    prefixes=(target, source_dir, ROOT),
                )
                evidence_path.write_text(text, encoding="utf-8")
                evidence_files.append(evidence_path)
        replay = portable_value(replay, prefixes=(target, source_dir, ROOT))
        replay = replace_value(replay, "build/", "evidence/")
        replay_path.write_text(
            json.dumps(replay, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        shutil.rmtree(build_dir, ignore_errors=True)

        artifact_files = [
            target / name
            for name in (
                "design.sv",
                "prompt.md",
                "task.toml",
                "tb.sv",
                support_name,
                "manifest.toml",
                "report.json",
                "generation.json",
            )
        ] + evidence_files
        provenance = {
            "schema_version": "2.0",
            "run_id": run_id,
            "task_id": task_id,
            "model_configuration": model,
            "evaluator_source_digest": evaluator_digest,
            "files": {
                path.relative_to(target).as_posix(): sha256(path)
                for path in artifact_files
            },
            "candidate_bundle_digest": canonical_file_set_digest(target, artifact_files),
        }
        (target / "provenance.json").write_text(
            json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        lint = [
            item for item in oracle_results(replay) if item["oracle_class"] == "lint"
        ]
        contributing = [
            item for item in oracle_results(replay) if item["contributes_to_gap"]
        ]
        rules = sorted(
            {
                rule
                for item in contributing
                for rule in item.get("coverage", {}).get("rules", [])
            }
        )
        finding_rules = sorted(
            {
                finding["rule_id"]
                for item in contributing
                for finding in item.get("findings", [])
            }
        )
        row = {
            "run_id": run_id,
            "model_configuration": model,
            "sample": generation["sample"],
            "task_id": task_id,
            "oracle_class": "+".join(
                sorted({item["oracle_class"] for item in contributing})
            ),
            "configured_rules": "+".join(rules),
            "functional": replay["functional"]["status"],
            "contributing_oracle": contributing_oracle_status(replay),
            "gap_member": bool(replay["gap_member"]),
            "finding_rules": "+".join(finding_rules),
            "lint": combined_status(item["status"] for item in lint),
            "lint_findings": sum(len(item.get("findings", [])) for item in lint),
        }
        csv_rows.append(row)
        index.append(
            {
                **row,
                "bundle_digest": provenance["candidate_bundle_digest"],
            }
        )

    analysis = analyze_reports(
        sorted(candidates_root.glob("*/*/report.json")),
        bootstrap_replicates=100_000,
        bootstrap_seed=20_260_824,
    )
    (output / "analysis.json").write_text(
        json.dumps(analysis, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    with (output / "candidate-outcomes.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)
    shutil.copy2(taskpack / "freeze.json", output / "taskpack-freeze.json")
    (output / "LICENSE.generated-rtl").write_text(
        """Generated RTL artifact license

To the extent the generated RTL and accompanying artifact metadata are subject
to copyright owned or controlled by the project author, they are licensed under
the Apache License, Version 2.0, included in the SV-Gap repository. Model names
identify generation provenance and do not imply provider endorsement.
""",
        encoding="utf-8",
    )
    overall = analysis["overall"]
    interval = overall["task_cluster_bootstrap"]
    (output / "README.md").write_text(
        f"""# Contract-oracle multi-model study v0.1

This artifact freezes 48 unrepaired candidates: eight task clusters, three
model configurations, and two fresh calls per model-task cell. The tasks cover
ready/valid persistence, bounded response, exactly one-cycle pulses, and
synthesized-reference equivalence. Each bundle contains the prompt, normalized
RTL, finite Icarus smoke test, property/reference source, multi-oracle report,
generation metadata, selected formal evidence, and content hashes.

Of 48 candidates, {overall['functional_statuses'].get('pass', 0)} pass the
functional smoke tests. {overall['determinate_functional_passes']} of those
receive a determinate contributing-oracle result, and {overall['gap_members']}
are gap members. The descriptive fraction is
`{overall['gap_members']}/{overall['determinate_functional_passes']} =
{overall['gap_fraction']:.1%}`. Resampling all candidates within each task as a
cluster gives a 95% percentile interval of `{interval['lower']:.1%}` to
`{interval['upper']:.1%}`. Because the eight tasks were hand-authored, this is a
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
""",
        encoding="utf-8",
    )
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "candidate_count": len(index),
                "task_count": 8,
                "model_configuration_count": 3,
                "samples_per_model_task": 2,
                "evaluator_source_digest": evaluator_digest,
                "taskpack_digest": json.loads(
                    (taskpack / "freeze.json").read_text(encoding="utf-8")
                )["canonical_digest"],
                "candidates": index,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"candidates   {len(index)}")
    print(f"gaps         {overall['gap_members']}/{overall['determinate_functional_passes']}")
    print(f"output       {output}")
    print(f"manifest     {sha256(output / 'manifest.json')}")
    return 0


def assert_same_outcome(
    source: dict[str, Any], replay: dict[str, Any], *, run_id: str, task_id: str
) -> None:
    source_oracles = {
        item["oracle_id"]: (item["status"], sorted(f["rule_id"] for f in item["findings"]))
        for item in oracle_results(source)
    }
    replay_oracles = {
        item["oracle_id"]: (item["status"], sorted(f["rule_id"] for f in item["findings"]))
        for item in oracle_results(replay)
    }
    source_outcome = (
        source["functional"]["status"],
        bool(source["gap_member"]),
        source_oracles,
    )
    replay_outcome = (
        replay["functional"]["status"],
        bool(replay["gap_member"]),
        replay_oracles,
    )
    if source_outcome != replay_outcome:
        raise SystemExit(
            f"replay outcome changed for {run_id}/{task_id}: "
            f"source={source_outcome!r} replay={replay_outcome!r}"
        )


def portable_value(value: Any, *, prefixes: tuple[Path, ...]) -> Any:
    if isinstance(value, dict):
        return {key: portable_value(item, prefixes=prefixes) for key, item in value.items()}
    if isinstance(value, list):
        return [portable_value(item, prefixes=prefixes) for item in value]
    if isinstance(value, str):
        return portable_text(value, prefixes=prefixes)
    return value


def portable_text(value: str, *, prefixes: tuple[Path, ...]) -> str:
    result = value
    for prefix in prefixes:
        for spelling in {str(prefix.resolve()), prefix.resolve().as_posix()}:
            result = result.replace(spelling + "/", "").replace(spelling, ".")
    result = re.sub(
        r"/(?:private/)?var/folders/[^\s\"']+", "<TEMP_PATH>", result
    )
    result = re.sub(r"/(?:private/)?tmp/[^\s\"']+", "<TEMP_PATH>", result)
    return result


def replace_value(value: Any, old: str, new: str) -> Any:
    if isinstance(value, dict):
        return {key: replace_value(item, old, new) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_value(item, old, new) for item in value]
    if isinstance(value, str):
        return value.replace(old, new)
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
