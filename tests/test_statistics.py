import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from svgap.statistics import analyze_reports, quantile


class ClusteredStatisticsTests(TestCase):
    def test_resamples_whole_tasks_and_excludes_tool_errors(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [
                write_report(root, "model-a--sample-01", "task-a", "pass", "fail", True),
                write_report(root, "model-b--sample-01", "task-a", "pass", "fail", True),
                write_report(root, "model-a--sample-01", "task-b", "pass", "pass", False),
                write_report(root, "model-b--sample-01", "task-b", "pass", "pass", False),
                write_report(root, "model-c--sample-01", "task-b", "pass", "tool_error", False),
            ]
            result = analyze_reports(paths, bootstrap_replicates=10_000, bootstrap_seed=7)
        self.assertEqual(result["overall"]["determinate_functional_passes"], 4)
        self.assertEqual(result["overall"]["gap_members"], 2)
        interval = result["overall"]["task_cluster_bootstrap"]
        self.assertEqual(interval["cluster_count"], 2)
        self.assertEqual(interval["estimate"], 0.5)
        self.assertEqual(interval["lower"], 0.0)
        self.assertEqual(interval["upper"], 1.0)
        self.assertEqual(result["lint_on_gap_members"]["statuses"], {"pass": 2})

    def test_linear_quantile(self) -> None:
        self.assertEqual(quantile([0.0, 1.0], 0.25), 0.25)


def write_report(
    root: Path,
    run_id: str,
    task: str,
    functional: str,
    oracle: str,
    gap: bool,
) -> Path:
    path = root / run_id / task / "report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "2.0",
        "candidate_id": task,
        "manifest": "manifest.toml",
        "functional": {
            "status": functional,
            "commands": [],
            "returncodes": [],
            "stdout": "",
            "stderr": "",
            "tool_versions": {},
            "imported_from": None,
            "evidence": {},
        },
        "oracle_results": [
            {
                "oracle_id": "specialized",
                "oracle_class": "temporal",
                "contributes_to_gap": True,
                "required": True,
                "status": oracle,
                "backend": "test",
                "backend_version": "1",
                "findings": (
                    [
                        {
                            "rule_id": "TEST-001",
                            "severity": "error",
                            "message": "finding",
                            "evidence": {},
                        }
                    ]
                    if oracle == "fail"
                    else []
                ),
                "diagnostics": [],
                "tool_versions": {},
                "coverage": {"rules": ["TEST-001"]},
            },
            {
                "oracle_id": "lint",
                "oracle_class": "lint",
                "contributes_to_gap": False,
                "required": False,
                "status": "pass",
                "backend": "lint",
                "backend_version": "1",
                "findings": [],
                "diagnostics": [],
                "tool_versions": {},
                "coverage": {},
            },
        ],
        "gap_member": gap,
        "generated_at": "2026-01-01T00:00:00+00:00",
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path
