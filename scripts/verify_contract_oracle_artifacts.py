#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from svgap.provenance import canonical_file_set_digest
from svgap.statistics import analyze_reports, combined_status
from svgap.validation import (
    contributing_oracle_status,
    oracle_results,
    validate_report_payload,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = ROOT / "artifacts/contract-oracle-study-v0.1"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path, default=DEFAULT_ARTIFACT)
    args = parser.parse_args()
    count = verify(args.artifact.resolve())
    print(f"verified     {count} candidates")
    print(f"artifact     {args.artifact.resolve()}")
    return 0


def verify(artifact: Path) -> int:
    manifest = json.loads((artifact / "manifest.json").read_text(encoding="utf-8"))
    candidates = manifest["candidates"]
    if manifest["candidate_count"] != 48 or len(candidates) != 48:
        raise ValueError("contract-oracle artifact must index exactly 48 candidates")
    indexed = {(item["run_id"], item["task_id"]) for item in candidates}
    actual = {
        (path.parent.parent.name, path.parent.name)
        for path in (artifact / "candidates").glob("*/*/report.json")
    }
    if indexed != actual:
        raise ValueError(
            f"candidate directories differ from index: missing={sorted(indexed - actual)} "
            f"extra={sorted(actual - indexed)}"
        )
    report_paths: list[Path] = []
    for item in candidates:
        directory = artifact / "candidates" / item["run_id"] / item["task_id"]
        provenance = json.loads(
            (directory / "provenance.json").read_text(encoding="utf-8")
        )
        files = [directory / relative for relative in provenance["files"]]
        actual_files = {
            path.relative_to(directory).as_posix()
            for path in directory.rglob("*")
            if path.is_file() and path.name != "provenance.json"
        }
        if actual_files != set(provenance["files"]):
            raise ValueError(f"unexpected candidate file set: {directory}")
        for path in files:
            if not path.is_file():
                raise ValueError(f"missing artifact file: {path}")
            if hashlib.sha256(path.read_bytes()).hexdigest() != provenance["files"][
                path.relative_to(directory).as_posix()
            ]:
                raise ValueError(f"hash mismatch: {path}")
        bundle = canonical_file_set_digest(directory, files)
        if bundle != provenance["candidate_bundle_digest"] or bundle != item["bundle_digest"]:
            raise ValueError(f"candidate bundle mismatch: {directory}")
        report_path = directory / "report.json"
        report = validate_report_payload(json.loads(report_path.read_text(encoding="utf-8")))
        lint = [
            oracle for oracle in oracle_results(report) if oracle["oracle_class"] == "lint"
        ]
        observed = {
            "functional": report["functional"]["status"],
            "contributing_oracle": contributing_oracle_status(report),
            "gap_member": bool(report["gap_member"]),
            "lint": combined_status(oracle["status"] for oracle in lint),
            "lint_findings": sum(len(oracle.get("findings", [])) for oracle in lint),
        }
        for key, value in observed.items():
            if item[key] != value:
                raise ValueError(f"indexed {key} mismatch: {directory}")
        report_paths.append(report_path)
    analysis = analyze_reports(
        report_paths,
        bootstrap_replicates=100_000,
        bootstrap_seed=20_260_824,
    )
    frozen_analysis = json.loads((artifact / "analysis.json").read_text(encoding="utf-8"))
    if analysis != frozen_analysis:
        raise ValueError("clustered analysis does not reproduce")
    scan_portability(artifact)
    return len(candidates)


def scan_portability(artifact: Path) -> None:
    forbidden = (
        "/Users/",
        "/home/",
        "/var/folders/",
        "/private/tmp/",
        "/tmp/",
        "release_staging/",
        str(ROOT.resolve()),
    )
    for path in artifact.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(value in text for value in forbidden):
            raise ValueError(f"nonportable path in {path}")


if __name__ == "__main__":
    raise SystemExit(main())
