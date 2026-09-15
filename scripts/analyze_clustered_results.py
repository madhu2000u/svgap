#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from svgap.statistics import analyze_reports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replicates", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=20_260_824)
    args = parser.parse_args()
    report_paths: list[Path] = []
    for root in args.roots:
        if root.is_file() and root.name == "report.json":
            report_paths.append(root)
        else:
            report_paths.extend(root.rglob("report.json"))
    report_paths = [path for path in report_paths if "build" not in path.parts]
    result = analyze_reports(
        report_paths,
        bootstrap_replicates=args.replicates,
        bootstrap_seed=args.seed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    overall = result["overall"]
    interval = overall["task_cluster_bootstrap"]
    print(f"reports       {overall['reports']}")
    print(f"functional    {overall['functional_statuses']}")
    print(f"determinate   {overall['determinate_functional_passes']}")
    print(f"gaps          {overall['gap_members']}")
    if interval:
        print(
            "clustered     "
            f"{interval['estimate']:.4f} "
            f"[{interval['lower']:.4f}, {interval['upper']:.4f}]"
        )
    print(f"output        {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
