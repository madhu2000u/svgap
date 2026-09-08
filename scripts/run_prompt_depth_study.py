#!/usr/bin/env python3
"""Run matched prompt-depth generations, oracle feedback, and fresh verification."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import time
import tomllib
from typing import Any

from run_generation_pilot import generate, provider_version
from svgap.api import evaluate
from svgap.pilot import load_task, materialize_candidate, resolve_prompt
from svgap.prompt_depth import repair_prompt, report_outcome, summarize_prompt_depth
from svgap.provenance import canonical_tree_digest


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASK_ROOT = ROOT / "taskpacks/real-fix-prompt-depth-v0.1"
DEFAULT_MATRIX = ROOT / "studies/prompt-depth-v0.1/model-matrix.json"
DEFAULT_OUTPUT = ROOT / "reports/generated/prompt-depth-v0.1"


@dataclass(frozen=True)
class Configuration:
    label: str
    provider: str
    model: str | None
    options: dict[str, Any]
    command: str | None = None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--taskpack", type=Path, default=DEFAULT_TASK_ROOT)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--tasks", nargs="+")
    parser.add_argument(
        "--levels",
        nargs="+",
        type=int,
        choices=(0, 1, 2, 3),
        default=(0, 1, 2, 3),
    )
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--repair",
        action="store_true",
        help="repair the earliest functional-pass/oracle-fail candidate per model-task",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="reuse complete reports and generation failures already recorded",
    )
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="save model responses without materializing or evaluating them",
    )
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be positive")

    taskpack = args.taskpack.resolve()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()) and not args.resume:
        parser.error(f"output is nonempty; pass --resume to continue: {output}")
    output.mkdir(parents=True, exist_ok=True)
    configurations = load_matrix(args.matrix.resolve())
    task_dirs = select_tasks(taskpack, args.tasks)
    levels = sorted(set(args.levels))
    write_study_contract(output, taskpack, args.matrix.resolve(), configurations, task_dirs, levels)

    prior = load_records(output / "study-records.jsonl") if args.resume else []
    existing_keys = {record_key(record) for record in prior}
    jobs = [
        (configuration, task_dir, level)
        for configuration in configurations
        for task_dir in task_dirs
        for level in levels
        if ("initial", configuration.label, task_dir.name, f"level_{level}")
        not in existing_keys
    ]
    records = list(prior)
    print(
        f"initial cells {len(configurations)} models x {len(task_dirs)} tasks x "
        f"{len(levels)} levels; {len(jobs)} pending"
    )
    records.extend(
        run_jobs(
            jobs,
            args.workers,
            lambda item: run_initial(
                item[0], item[1], item[2], output, args.generate_only
            ),
        )
    )
    write_records(output / "study-records.jsonl", records)

    if args.repair and not args.generate_only:
        repair_jobs = select_repair_jobs(records, configurations, task_dirs)
        repair_jobs = [
            job
            for job in repair_jobs
            if ("repair", job[0].label, job[1].name, job[2]["prompt_level"])
            not in {record_key(record) for record in records}
        ]
        print(f"repair cells {len(repair_jobs)} pending")
        records.extend(
            run_jobs(
                repair_jobs,
                args.workers,
                lambda item: run_repair(item[0], item[1], item[2], output),
            )
        )
        write_records(output / "study-records.jsonl", records)

    summary = summarize_prompt_depth(records)
    (output / "prompt-depth-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"records      {len(records)}")
    print(f"summary      {output / 'prompt-depth-summary.json'}")
    failures = sum(record.get("generation_status") != "ok" for record in records)
    return 2 if failures else 0


def load_matrix(path: Path) -> list[Configuration]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("configurations")
    if not isinstance(raw, list) or not raw:
        raise ValueError("model matrix must contain a nonempty configurations array")
    configurations = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("model configuration must be an object")
        provider = str(item["provider"])
        if provider not in {"codex", "ollama", "claude", "command"}:
            raise ValueError(f"unsupported provider in model matrix: {provider}")
        configurations.append(
            Configuration(
                label=str(item["label"]),
                provider=provider,
                model=str(item["model"]) if item.get("model") is not None else None,
                options=dict(item.get("options", {})),
                command=str(item["command"]) if item.get("command") else None,
            )
        )
    labels = [item.label for item in configurations]
    if len(labels) != len(set(labels)):
        raise ValueError("model configuration labels must be unique")
    return configurations


def select_tasks(taskpack: Path, selected: list[str] | None) -> list[Path]:
    tasks_root = taskpack / "tasks"
    available = {path.name: path for path in tasks_root.iterdir() if path.is_dir()}
    names = selected or sorted(available)
    unknown = sorted(set(names) - set(available))
    if unknown:
        raise ValueError(f"unknown tasks: {', '.join(unknown)}")
    return [available[name] for name in names]


def run_jobs(jobs: list[Any], workers: int, function: Any) -> list[dict[str, Any]]:
    if workers == 1:
        records = []
        for index, job in enumerate(jobs, 1):
            record = function(job)
            records.append(record)
            print_progress(index, len(jobs), record)
        return records
    records = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(function, job): job for job in jobs}
        for index, future in enumerate(as_completed(futures), 1):
            try:
                record = future.result()
            except Exception as exc:  # retain a visible orchestration failure
                job = futures[future]
                configuration, task_dir = job[0], job[1]
                level = job[2] if isinstance(job[2], int) else job[2]["prompt_ordinal"]
                record = base_record(
                    "initial",
                    configuration,
                    task_dir,
                    level,
                    generation_status="orchestration_error",
                    error=str(exc),
                )
            records.append(record)
            print_progress(index, len(jobs), record)
    return records


def run_initial(
    configuration: Configuration,
    task_dir: Path,
    level: int,
    output: Path,
    generate_only: bool,
) -> dict[str, Any]:
    task = load_task(task_dir)
    prompt_path, _ = resolve_prompt(task_dir, task, f"level_{level}")
    prompt = prompt_path.read_text(encoding="utf-8")
    return generate_and_evaluate(
        phase="initial",
        configuration=configuration,
        task_dir=task_dir,
        level=level,
        prompt=prompt,
        output=output,
        generate_only=generate_only,
    )


def run_repair(
    configuration: Configuration,
    task_dir: Path,
    parent: dict[str, Any],
    output: Path,
) -> dict[str, Any]:
    level = int(parent["prompt_ordinal"])
    task = load_task(task_dir)
    prompt_path, _ = resolve_prompt(task_dir, task, str(parent["prompt_level"]))
    report = json.loads((output / parent["report_path"]).read_text(encoding="utf-8"))
    candidate = (output / parent["design_path"]).read_text(encoding="utf-8")
    prompt = repair_prompt(prompt_path.read_text(encoding="utf-8"), candidate, report)
    return generate_and_evaluate(
        phase="repair",
        configuration=configuration,
        task_dir=task_dir,
        level=level,
        prompt=prompt,
        output=output,
        generate_only=False,
        parent=parent,
    )


def generate_and_evaluate(
    *,
    phase: str,
    configuration: Configuration,
    task_dir: Path,
    level: int,
    prompt: str,
    output: Path,
    generate_only: bool,
    parent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    started = time.monotonic()
    record = base_record(
        phase,
        configuration,
        task_dir,
        level,
        generation_status="started",
    )
    run_id = f"{configuration.label}--level-{level}"
    phase_root = output / phase
    response_dir = phase_root / "_responses" / run_id
    response_dir.mkdir(parents=True, exist_ok=True)
    suffix = "repair" if phase == "repair" else "initial"
    response_path = response_dir / f"{task_dir.name}.{suffix}.txt"
    try:
        with tempfile.TemporaryDirectory(prefix="svgap-prompt-depth-") as directory:
            response, command = generate(
                configuration.provider,
                configuration.model,
                prompt,
                Path(directory),
                configuration.command,
                sample=int(configuration.options.get("sample", 1)),
                ollama_temperature=configuration.options.get("temperature"),
                ollama_seed_base=configuration.options.get("seed_base"),
                codex_reasoning_effort=configuration.options.get("reasoning_effort"),
            )
    except Exception as exc:
        record.update(
            generation_status="generation_error",
            error=str(exc),
            elapsed_seconds=round(time.monotonic() - started, 6),
        )
        return record
    response_path.write_text(response, encoding="utf-8")
    generation = {
        "schema_version": "1.0",
        "phase": phase,
        "provider": configuration.provider,
        "interface_version": provider_version(configuration.provider),
        "requested_model": configuration.model,
        "configuration_label": configuration.label,
        "generation_options": configuration.options,
        "task": task_dir.name,
        "prompt_level": f"level_{level}",
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }
    generation_path = response_path.with_suffix(".generation.json")
    generation_path.write_text(
        json.dumps(generation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    record.update(
        generation_status="ok",
        response_path=response_path.relative_to(output).as_posix(),
        generation_path=generation_path.relative_to(output).as_posix(),
        elapsed_seconds=generation["elapsed_seconds"],
    )
    if generate_only:
        return record
    try:
        manifest = materialize_candidate(
            task_dir,
            response_path,
            configuration.model or configuration.label,
            phase_root,
            run_id,
            prompt_level=f"level_{level}",
            prompt_override=prompt if phase == "repair" else None,
        )
        report = evaluate(
            manifest,
            manifest_label=manifest.relative_to(output).as_posix(),
        ).to_dict()
        shutil.copy2(generation_path, manifest.parent / "generation.json")
        record.update(report_outcome(report))
        record.update(
            manifest_path=manifest.relative_to(output).as_posix(),
            report_path=(manifest.parent / "report.json").relative_to(output).as_posix(),
            design_path=(manifest.parent / "design.sv").relative_to(output).as_posix(),
        )
        if parent is not None:
            record["parent"] = {
                "prompt_level": parent["prompt_level"],
                "response_path": parent["response_path"],
                "report_path": parent["report_path"],
            }
    except Exception as exc:
        record.update(generation_status="response_or_evaluation_error", error=str(exc))
    record["elapsed_seconds"] = round(time.monotonic() - started, 6)
    return record


def base_record(
    phase: str,
    configuration: Configuration,
    task_dir: Path,
    level: int,
    *,
    generation_status: str,
    error: str | None = None,
) -> dict[str, Any]:
    task = tomllib.loads((task_dir / "task.toml").read_text(encoding="utf-8"))
    result = {
        "schema_version": "1.0",
        "phase": phase,
        "configuration_label": configuration.label,
        "provider": configuration.provider,
        "requested_model": configuration.model,
        "generation_options": configuration.options,
        "task_id": task_dir.name,
        "category": task.get("category"),
        "oracle_class": task.get("oracle_class"),
        "prompt_level": f"level_{level}",
        "prompt_ordinal": level,
        "generation_status": generation_status,
    }
    if error:
        result["error"] = error
    return result


def select_repair_jobs(
    records: list[dict[str, Any]],
    configurations: list[Configuration],
    task_dirs: list[Path],
) -> list[tuple[Configuration, Path, dict[str, Any]]]:
    configuration_map = {item.label: item for item in configurations}
    task_map = {item.name: item for item in task_dirs}
    candidates: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for record in records:
        if record.get("phase") == "initial" and record.get("gap_member"):
            key = (str(record["configuration_label"]), str(record["task_id"]))
            candidates.setdefault(key, []).append(record)
    jobs = []
    for (label, task_id), rows in sorted(candidates.items()):
        parent = min(rows, key=lambda item: int(item["prompt_ordinal"]))
        jobs.append((configuration_map[label], task_map[task_id], parent))
    return jobs


def write_study_contract(
    output: Path,
    taskpack: Path,
    matrix: Path,
    configurations: list[Configuration],
    task_dirs: list[Path],
    levels: list[int],
) -> None:
    freeze = json.loads((taskpack / "freeze.json").read_text(encoding="utf-8"))
    actual = canonical_tree_digest(taskpack, exclude_names={"freeze.json"})
    if actual != freeze["canonical_digest"]:
        raise ValueError("taskpack digest does not match freeze.json")
    payload = {
        "schema_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "taskpack": {
            "path": str(taskpack),
            "canonical_digest": actual,
            "tasks": [path.name for path in task_dirs],
        },
        "matrix": {
            "path": str(matrix),
            "sha256": hashlib.sha256(matrix.read_bytes()).hexdigest(),
            "configurations": [item.label for item in configurations],
        },
        "levels": levels,
        "matched_inputs": ["interface", "smoke test", "hidden oracle", "reference"],
        "primary_estimand": "first observed contract-closing prompt depth per model-task",
        "ranking_policy": "no scalar leaderboard or rank ordering",
    }
    path = output / "study-contract.json"
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        for key in ("taskpack", "matrix", "levels"):
            if existing[key] != payload[key]:
                raise ValueError(f"resume contract mismatch in {key}")
        return
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_records(path: Path, records: list[dict[str, Any]]) -> None:
    unique = {record_key(record): record for record in records}
    ordered = [unique[key] for key in sorted(unique)]
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in ordered),
        encoding="utf-8",
    )
    temporary.replace(path)


def record_key(record: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(record["phase"]),
        str(record["configuration_label"]),
        str(record["task_id"]),
        str(record["prompt_level"]),
    )


def print_progress(index: int, total: int, record: dict[str, Any]) -> None:
    result = (
        "closed"
        if record.get("contract_closed")
        else "gap"
        if record.get("gap_member")
        else record.get("generation_status")
    )
    print(
        f"[{index:>3}/{total}] {record['configuration_label']} "
        f"{record['task_id']} {record['prompt_level']} {result}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
