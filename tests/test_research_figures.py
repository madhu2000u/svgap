from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from xml.etree import ElementTree

from scripts.build_research_figures import build_all


ROOT = Path(__file__).resolve().parents[1]


class ResearchFigureTests(TestCase):
    def test_builds_deterministic_valid_svg_figures_from_frozen_results(self) -> None:
        expected = {
            "benchmark-oracle-coverage.svg",
            "contract-study-by-task.svg",
            "evaluation-contract.svg",
            "task-clustered-intervals.svg",
        }
        with TemporaryDirectory() as directory:
            output = Path(directory)
            first = build_all(output, root=ROOT)
            first_payloads = {path.name: path.read_bytes() for path in first}
            second = build_all(output, root=ROOT)
            second_payloads = {path.name: path.read_bytes() for path in second}

        self.assertEqual(set(first_payloads), expected)
        self.assertEqual(first_payloads, second_payloads)
        for payload in first_payloads.values():
            root = ElementTree.fromstring(payload)
            self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertNotIn(b"/Users/", payload)

        task_figure = first_payloads["contract-study-by-task.svg"]
        self.assertIn(b"11 / 40 = 27.5%", task_figure)
        interval_figure = first_payloads["task-clustered-intervals.svg"]
        self.assertIn(b"7.3%", interval_figure)
        self.assertIn(b"48.8%", interval_figure)
