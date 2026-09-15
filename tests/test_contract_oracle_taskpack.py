import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from unittest import TestCase, skipUnless

from svgap.api import evaluate
from svgap.pilot import materialize_candidate
from svgap.provenance import canonical_tree_digest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "taskpacks/contract-oracles-v0.1"
HAS_TOOLS = all(shutil.which(tool) for tool in ("yosys", "iverilog", "vvp"))


@skipUnless(HAS_TOOLS, "Yosys and Icarus Verilog are required")
class ContractOracleTaskpackTests(TestCase):
    def test_safe_and_unsafe_references_calibrate(self) -> None:
        tasks = sorted(path for path in (PACK / "tasks").iterdir() if path.is_dir())
        self.assertEqual(len(tasks), 8)
        for task in tasks:
            expected_rule = _task_rule(task)
            for variant, expected in (("safe", "pass"), ("unsafe", "fail")):
                with self.subTest(task=task.name, variant=variant):
                    with TemporaryDirectory() as directory:
                        response = Path(directory) / "response.sv"
                        response.write_text(
                            (task / f"reference-{variant}.sv").read_text(encoding="utf-8"),
                            encoding="utf-8",
                        )
                        manifest = materialize_candidate(
                            task, response, "calibration", Path(directory) / "runs"
                        )
                        report = evaluate(manifest).to_dict()
                        self.assertEqual(report["functional"]["status"], "pass", report)
                        contributing = [
                            item
                            for item in report["oracle_results"]
                            if item["contributes_to_gap"]
                        ]
                        self.assertEqual(len(contributing), 1)
                        self.assertEqual(contributing[0]["status"], expected, report)
                        if variant == "unsafe":
                            self.assertIn(
                                expected_rule,
                                {item["rule_id"] for item in contributing[0]["findings"]},
                            )

    def test_frozen_digest_is_stable(self) -> None:
        freeze = json.loads((PACK / "freeze.json").read_text(encoding="utf-8"))
        self.assertEqual(
            canonical_tree_digest(PACK, exclude_names={"freeze.json"}),
            freeze["canonical_digest"],
        )


def _task_rule(task: Path) -> str:
    for line in (task / "task.toml").read_text(encoding="utf-8").splitlines():
        if line.startswith("rule_id = "):
            return line.split('"', 2)[1]
    raise AssertionError(f"missing rule_id in {task}")
