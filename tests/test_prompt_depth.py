from unittest import TestCase

from svgap.prompt_depth import repair_prompt, summarize_prompt_depth


class PromptDepthTests(TestCase):
    def test_summary_preserves_censoring_and_non_monotone_outcomes(self) -> None:
        records = []
        for model, outcomes in (("deep", [False, True, True, True]), ("shallow", [False] * 4)):
            for level, closed in enumerate(outcomes):
                records.append(
                    {
                        "phase": "initial",
                        "configuration_label": model,
                        "provider": "fixture",
                        "requested_model": model,
                        "task_id": "task",
                        "category": "temporal",
                        "prompt_level": f"level_{level}",
                        "prompt_ordinal": level,
                        "generation_status": "ok",
                        "functional_status": "pass",
                        "contributing_oracle_status": "pass" if closed else "fail",
                        "contract_closed": closed,
                    }
                )
        summary = summarize_prompt_depth(records)
        self.assertEqual(
            summary["configurations"]["deep"]["depth_distribution"]["1"], 1
        )
        self.assertEqual(
            summary["configurations"]["shallow"]["depth_distribution"]["censored"],
            1,
        )
        self.assertTrue(summary["not_a_leaderboard"])

    def test_repair_prompt_exposes_finding_but_not_hidden_evidence(self) -> None:
        report = {
            "functional": {"status": "pass"},
            "oracle_results": [
                {
                    "contributes_to_gap": True,
                    "oracle_class": "temporal",
                    "status": "fail",
                    "findings": [
                        {
                            "rule_id": "REF-TEMP-001",
                            "message": "response was early",
                            "evidence": {"counterexample": "hidden.vcd"},
                        }
                    ],
                }
            ],
        }
        prompt = repair_prompt("Implement module x;", "module x; endmodule", report)
        self.assertIn("REF-TEMP-001", prompt)
        self.assertIn("response was early", prompt)
        self.assertNotIn("hidden.vcd", prompt)

