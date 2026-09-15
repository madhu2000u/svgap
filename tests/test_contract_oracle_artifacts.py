from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from scripts.export_contract_oracle_artifacts import portable_text
from scripts.verify_contract_oracle_artifacts import scan_portability, verify


ROOT = Path(__file__).resolve().parents[1]


class ContractOracleArtifactTests(TestCase):
    def test_public_artifact_hashes_outcomes_and_analysis(self) -> None:
        artifact = ROOT / "artifacts/contract-oracle-study-v0.1"
        if not artifact.is_dir():
            self.skipTest("contract-oracle public artifact has not been exported")
        self.assertEqual(verify(artifact), 48)

    def test_portability_scan_includes_vcd_counterexamples(self) -> None:
        with TemporaryDirectory() as directory:
            artifact = Path(directory)
            evidence = artifact / "counterexample.vcd"
            evidence.write_text("$comment /Users/example/private $end\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "nonportable path"):
                scan_portability(artifact)

    def test_portability_scan_rejects_transient_tool_paths(self) -> None:
        with TemporaryDirectory() as directory:
            artifact = Path(directory)
            report = artifact / "report.json"
            report.write_text('{"stderr":"/var/folders/example/tool"}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "nonportable path"):
                scan_portability(artifact)

    def test_export_normalizes_transient_tool_paths(self) -> None:
        payload = portable_text(
            'tool -F"/var/folders/example/args" and /private/tmp/work/output',
            prefixes=(),
        )
        self.assertEqual(payload, 'tool -F"<TEMP_PATH>" and <TEMP_PATH>')
