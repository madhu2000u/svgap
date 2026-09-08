#!/usr/bin/env python3
"""Build deterministic, publication-ready SVG figures from frozen results."""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "assets" / "research"

INK = "#172033"
MUTED = "#5E6B7D"
FAINT = "#E8EDF4"
PANEL = "#F7F9FC"
BLUE = "#356AE6"
BLUE_LIGHT = "#E8F0FF"
TEAL = "#1F9D8A"
TEAL_LIGHT = "#DDF5F0"
ORANGE = "#D7653B"
ORANGE_LIGHT = "#FBE9E1"
AMBER = "#D49B28"
AMBER_LIGHT = "#FFF3D6"
GRAY = "#A9B4C3"
GRAY_LIGHT = "#EEF2F6"
WHITE = "#FFFFFF"


class Canvas:
    def __init__(self, width: int, height: int, title: str, description: str):
        self.width = width
        self.height = height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
            f'aria-labelledby="title desc">',
            f"<title id=\"title\">{escape(title)}</title>",
            f"<desc id=\"desc\">{escape(description)}</desc>",
            """<defs>
  <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#172033" flood-opacity="0.10"/>
  </filter>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">
    <path d="M0,0 L10,5 L0,10 z" fill="#8793A5"/>
  </marker>
  <style>
    text { font-family: Inter, "IBM Plex Sans", Helvetica, Arial, sans-serif; fill: #172033; }
    .title { font-size: 30px; font-weight: 700; letter-spacing: -0.5px; }
    .subtitle { font-size: 16px; fill: #5E6B7D; }
    .heading { font-size: 17px; font-weight: 700; }
    .body { font-size: 15px; }
    .small { font-size: 13px; fill: #5E6B7D; }
    .tiny { font-size: 11px; fill: #5E6B7D; }
    .number { font-size: 25px; font-weight: 750; }
    .mono { font-family: "IBM Plex Mono", Menlo, Consolas, monospace; }
  </style>
</defs>""",
            f'<rect width="{width}" height="{height}" fill="{WHITE}"/>',
        ]

    def rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        *,
        fill: str = WHITE,
        stroke: str = FAINT,
        radius: float = 14,
        stroke_width: float = 1,
        shadow: bool = False,
        opacity: float = 1,
    ) -> None:
        extra = ' filter="url(#shadow)"' if shadow else ""
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'rx="{radius}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{stroke_width}" opacity="{opacity}"{extra}/>'
        )

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        *,
        stroke: str = GRAY,
        width: float = 2,
        dash: str | None = None,
        arrow: bool = False,
    ) -> None:
        attrs = f' stroke-dasharray="{dash}"' if dash else ""
        if arrow:
            attrs += ' marker-end="url(#arrow)"'
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{width}"{attrs}/>'
        )

    def text(
        self,
        x: float,
        y: float,
        value: str,
        *,
        cls: str = "body",
        anchor: str = "start",
        fill: str | None = None,
        weight: int | None = None,
    ) -> None:
        attrs = f' class="{cls}" text-anchor="{anchor}"'
        if fill:
            attrs += f' fill="{fill}" style="fill:{fill}"'
        if weight:
            attrs += f' font-weight="{weight}"'
        self.parts.append(f'<text x="{x}" y="{y}"{attrs}>{escape(value)}</text>')

    def circle(
        self,
        x: float,
        y: float,
        radius: float,
        *,
        fill: str,
        stroke: str = WHITE,
        stroke_width: float = 3,
    ) -> None:
        self.parts.append(
            f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )

    def path(self, data: str, *, stroke: str, width: float = 2) -> None:
        self.parts.append(
            f'<path d="{data}" fill="none" stroke="{stroke}" '
            f'stroke-width="{width}" marker-end="url(#arrow)"/>'
        )

    def finish(self) -> str:
        return "\n".join([*self.parts, "</svg>", ""])


def add_title(canvas: Canvas, title: str, subtitle: str) -> None:
    canvas.text(60, 58, title, cls="title")
    canvas.text(60, 88, subtitle, cls="subtitle")


def write_svg(output_dir: Path, name: str, canvas: Canvas) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / name
    path.write_text(canvas.finish(), encoding="utf-8")
    return path


def evaluation_contract(output_dir: Path) -> Path:
    canvas = Canvas(
        1280,
        720,
        "SV-Gap evaluation contract",
        "A candidate RTL design is evaluated by a functional harness, a contributing specialized oracle, and contextual lint before a schema-versioned evidence report is produced.",
    )
    add_title(
        canvas,
        "One candidate, several independent questions",
        "SV-Gap preserves functional evidence and adds only the production contracts explicitly declared by the task.",
    )

    canvas.rect(55, 145, 200, 400, fill=PANEL, shadow=True)
    canvas.text(80, 182, "Task contract", cls="heading")
    for y, label, detail in [
        (230, "Prompt", "required behavior"),
        (300, "Intent", "clock, reset, state"),
        (370, "Property", "protocol / temporal"),
        (440, "Reference", "equivalence target"),
        (510, "Policy", "which oracle contributes"),
    ]:
        canvas.circle(83, y - 5, 5, fill=BLUE, stroke=BLUE, stroke_width=0)
        canvas.text(100, y, label, weight=700)
        canvas.text(100, y + 21, detail, cls="small")

    canvas.line(260, 345, 300, 345, arrow=True)
    canvas.rect(310, 245, 205, 200, fill=BLUE_LIGHT, stroke="#B8CCFF", shadow=True)
    canvas.text(412, 285, "Candidate RTL", cls="heading", anchor="middle")
    canvas.text(412, 325, "generated or supplied", cls="small", anchor="middle")
    canvas.rect(345, 355, 135, 48, fill=WHITE, stroke="#B8CCFF", radius=8)
    canvas.text(412, 385, "design.sv", cls="body mono", anchor="middle")

    branch_x = 552
    canvas.line(515, 345, branch_x, 345)
    canvas.line(branch_x, 210, branch_x, 480)
    for y in (210, 345, 480):
        canvas.line(branch_x, y, 590, y, arrow=True)

    evidence = [
        (135, BLUE_LIGHT, "#B8CCFF", BLUE, "Functional harness", "Icarus simulation", "pass / fail / compile error"),
        (270, ORANGE_LIGHT, "#F1BBA5", ORANGE, "Specialized oracle", "CDC · RDC · protocol · temporal · equivalence", "contributes to gap when configured"),
        (405, GRAY_LIGHT, "#D1D9E4", MUTED, "Ordinary RTL lint", "Verilator or Verible", "contextual; never silently substitutes"),
    ]
    for y, fill, stroke, accent, heading, detail, policy in evidence:
        canvas.rect(595, y, 295, 110, fill=fill, stroke=stroke, radius=12)
        canvas.rect(595, y, 8, 110, fill=accent, stroke=accent, radius=4)
        canvas.text(622, y + 31, heading, cls="heading")
        canvas.text(622, y + 59, detail, cls="small")
        canvas.text(622, y + 84, policy, cls="small")

    for y in (190, 325, 460):
        canvas.path(f"M 890 {y} C 930 {y}, 930 345, 970 345", stroke=GRAY)

    canvas.rect(980, 145, 245, 400, fill=WHITE, stroke="#C8D2E1", shadow=True)
    canvas.text(1102, 182, "Evidence report", cls="heading", anchor="middle")
    canvas.text(1102, 207, "schema v2", cls="small mono", anchor="middle")
    report_rows = [
        (250, BLUE_LIGHT, BLUE, "functional"),
        (310, ORANGE_LIGHT, ORANGE, "oracle_results[]"),
        (370, GRAY_LIGHT, MUTED, "findings + provenance"),
    ]
    for y, fill, accent, label in report_rows:
        canvas.rect(1010, y - 30, 185, 44, fill=fill, stroke=fill, radius=7)
        canvas.circle(1029, y - 8, 5, fill=accent, stroke=accent, stroke_width=0)
        canvas.text(1044, y - 3, label, cls="small mono")
    canvas.rect(1008, 420, 188, 82, fill=INK, stroke=INK, radius=10)
    canvas.text(1102, 448, "gap member", cls="heading", anchor="middle", fill=WHITE)
    canvas.text(1102, 474, "functional pass", cls="small", anchor="middle", fill="#DCE5F3")
    canvas.text(1102, 492, "+ contributing fail", cls="small", anchor="middle", fill="#DCE5F3")

    canvas.rect(55, 603, 1170, 64, fill=PANEL, stroke=FAINT, radius=10)
    canvas.text(75, 630, "Interpretation", cls="heading")
    canvas.text(190, 630, "A lint pass is not a specialized-oracle pass. A tool error is not a pass. Only configured evidence defines membership.", cls="body")
    canvas.text(75, 652, "21 stable finding IDs · 22 paired calibration witnesses · open backends with explicit non-signoff boundaries", cls="small")
    return write_svg(output_dir, "evaluation-contract.svg", canvas)


def benchmark_oracle_coverage(output_dir: Path) -> Path:
    canvas = Canvas(
        1280,
        720,
        "Lower-bound oracle coverage audit",
        "Four categories of explicit production intent were found in a 508-task public RTL inventory, while none had recognizable scoring by the corresponding specialized oracle.",
    )
    add_title(
        canvas,
        "Explicit production intent, absent specialized scoring",
        "Conservative lower bounds in a frozen 508-task inventory: VerilogEval, RTLLM, and an audited open-tool CVDP subset.",
    )

    headers = [(60, "Category"), (430, "Contract-positive tasks"), (720, "Matching scored oracle"), (1000, "Observed coverage gap")]
    for x, label in headers:
        canvas.text(x, 140, label, cls="small", weight=700)
    canvas.line(60, 155, 1220, 155, stroke="#D8E0EB", width=1)

    rows = [
        ("CDC / RDC intent", "structural intent sufficient", 11, "CDC/RDC checker", "11 / 11"),
        ("Power-on state", "explicit initial-state contract", 28, "randomized / X-aware", "28 / 28"),
        ("Temporal correctness", "bounded, persistence, progress, protocol", 98, "native property / formal", "98 / 98"),
        ("Synthesis equivalence", "original RTL + synthesis required", 16, "equivalence / post-synth compare", "16 / 16"),
    ]
    for index, (category, detail, count, oracle, gap) in enumerate(rows):
        y = 175 + index * 112
        canvas.rect(50, y, 1180, 92, fill=PANEL if index % 2 == 0 else WHITE, stroke=FAINT, radius=10)
        canvas.text(72, y + 34, category, cls="heading")
        canvas.text(72, y + 61, detail, cls="small")
        canvas.text(430, y + 43, str(count), cls="number", fill=BLUE)
        canvas.text(475, y + 43, "/ 508", cls="body")
        canvas.rect(710, y + 21, 245, 48, fill=GRAY_LIGHT, stroke="#D5DCE6", radius=8)
        canvas.text(733, y + 51, "0", cls="number", fill=MUTED)
        canvas.text(770, y + 49, oracle, cls="small")
        canvas.rect(990, y + 21, 210, 48, fill=ORANGE_LIGHT, stroke="#F1BBA5", radius=8)
        canvas.text(1095, y + 51, gap, cls="heading", anchor="middle", fill=ORANGE)

    canvas.rect(50, 636, 1180, 45, fill=AMBER_LIGHT, stroke="#EBCB82", radius=9)
    canvas.text(70, 664, "These are missing-evidence counts, not defective-design counts; finite simulation remains valuable but does not instantiate the named oracle.", cls="body")
    return write_svg(output_dir, "benchmark-oracle-coverage.svg", canvas)


def task_outcomes(output_dir: Path, analysis: dict) -> Path:
    canvas = Canvas(
        1280,
        800,
        "Expanded contract-oracle study outcomes by task",
        "Forty-eight candidates across eight task clusters are shown as specialized pass, gap member, functional pass with indeterminate specialized oracle, or functional nonpass.",
    )
    add_title(
        canvas,
        "Where the expanded oracles changed the answer",
        "48 fresh, unrepaired generations · 3 model configurations · 2 calls per model-task cell.",
    )

    legend = [
        (TEAL, "functional pass + oracle pass"),
        (ORANGE, "gap member"),
        (AMBER, "functional pass + indeterminate"),
        (GRAY, "functional nonpass"),
    ]
    x = 60
    for color, label in legend:
        canvas.rect(x, 112, 18, 18, fill=color, stroke=color, radius=4)
        canvas.text(x + 27, 126, label, cls="small")
        x += 255 if "indeterminate" not in label else 285
    canvas.text(1215, 126, "each block = 1 candidate", cls="tiny", anchor="end")

    task_order = [
        ("stream_hold", "Stream hold", "protocol"),
        ("result_hold", "Result hold", "protocol"),
        ("command_deadline", "Command deadline", "temporal"),
        ("grant_deadline", "Grant deadline", "temporal"),
        ("irq_pulse", "IRQ pulse", "temporal"),
        ("completion_pulse", "Completion pulse", "temporal"),
        ("opcode_unit", "Opcode unit", "equivalence"),
        ("signed_clamp", "Signed clamp", "equivalence"),
    ]
    class_style = {
        "protocol": (BLUE_LIGHT, BLUE),
        "temporal": (AMBER_LIGHT, "#956708"),
        "equivalence": (TEAL_LIGHT, "#087362"),
    }
    for index, (task_id, label, oracle_class) in enumerate(task_order):
        row = analysis["by_task"][task_id]
        reports = row["reports"]
        functional_passes = row["functional_statuses"].get("pass", 0)
        determinate = row["determinate_functional_passes"]
        gaps = row["gap_members"]
        counts = [
            (TEAL, determinate - gaps),
            (ORANGE, gaps),
            (AMBER, functional_passes - determinate),
            (GRAY, reports - functional_passes),
        ]
        if sum(count for _, count in counts) != reports:
            raise ValueError(f"outcome partition does not sum to {reports}: {task_id}")

        y = 160 + index * 72
        if index in (0, 2, 6):
            canvas.line(50, y - 14, 1220, y - 14, stroke="#E0E6EF", width=1)
        canvas.text(60, y + 31, label, cls="heading")
        badge_fill, badge_ink = class_style[oracle_class]
        canvas.rect(223, y + 10, 104, 28, fill=badge_fill, stroke=badge_fill, radius=14)
        canvas.text(275, y + 29, oracle_class, cls="tiny", anchor="middle", fill=badge_ink, weight=700)

        cells: list[str] = []
        for color, count in counts:
            cells.extend([color] * count)
        for cell_index, color in enumerate(cells):
            cell_x = 365 + cell_index * 82
            canvas.rect(cell_x, y, 66, 48, fill=color, stroke=color, radius=7)
        canvas.text(900, y + 22, f"{gaps} / {determinate}", cls="heading", fill=ORANGE if gaps else MUTED)
        canvas.text(980, y + 22, "gaps / determinate functional passes", cls="small")
        if functional_passes != reports:
            canvas.text(900, y + 43, f"{reports - functional_passes} functional nonpass", cls="tiny")

    overall = analysis["overall"]
    canvas.rect(50, 744, 1180, 40, fill=INK, stroke=INK, radius=9)
    canvas.text(70, 770, f"Overall: {overall['gap_members']} / {overall['determinate_functional_passes']} = {overall['gap_fraction'] * 100:.1f}%", cls="heading", fill=WHITE)
    canvas.text(460, 770, "All 11 gap members had Verilator lint status pass; equivalence was a 0 / 12 bounded null.", cls="body", fill="#DCE5F3")
    return write_svg(output_dir, "contract-study-by-task.svg", canvas)


def clustered_intervals(output_dir: Path, reset: dict, contract: dict) -> Path:
    canvas = Canvas(
        1280,
        620,
        "Task-clustered sensitivity intervals",
        "Point estimates and 95 percent nonparametric task-cluster bootstrap percentile intervals for reset-release and expanded contract-oracle studies.",
    )
    add_title(
        canvas,
        "Recurrence is task-clustered, not 120 independent Bernoulli trials",
        "All candidates from a sampled task move together. Intervals describe sensitivity to the finite task set, not population prevalence.",
    )

    left, right = 330, 1180
    axis_y = 505
    for percent in range(0, 61, 10):
        x = left + (right - left) * percent / 60
        canvas.line(x, 145, x, axis_y, stroke="#E2E8F0", width=1)
        canvas.text(x, axis_y + 28, f"{percent}%", cls="small", anchor="middle")
    canvas.line(left, axis_y, right, axis_y, stroke="#AEB9C7", width=1)

    studies = [
        ("Reset-release", reset, BLUE, "8 tasks · 72 candidates"),
        ("Expanded contracts", contract, ORANGE, "8 tasks · 48 candidates"),
    ]
    for index, (label, payload, color, detail) in enumerate(studies):
        y = 245 + index * 150
        overall = payload["overall"]
        interval = overall["task_cluster_bootstrap"]
        estimate = interval["estimate"] * 100
        lower = interval["lower"] * 100
        upper = interval["upper"] * 100
        scale = lambda value: left + (right - left) * value / 60
        canvas.text(60, y - 12, label, cls="heading")
        canvas.text(60, y + 15, detail, cls="small")
        canvas.text(60, y + 39, f"{overall['gap_members']} / {overall['determinate_functional_passes']} determinate functional passes", cls="small")
        canvas.line(scale(lower), y, scale(upper), y, stroke=color, width=8)
        canvas.line(scale(lower), y - 13, scale(lower), y + 13, stroke=color, width=3)
        canvas.line(scale(upper), y - 13, scale(upper), y + 13, stroke=color, width=3)
        canvas.circle(scale(estimate), y, 12, fill=color)
        canvas.rect(scale(estimate) - 53, y - 55, 106, 32, fill=color, stroke=color, radius=16)
        canvas.text(scale(estimate), y - 34, f"{estimate:.1f}%", cls="heading", anchor="middle", fill=WHITE)
        canvas.text(scale(lower), y + 35, f"{lower:.1f}%", cls="small", anchor="middle", fill=color, weight=700)
        canvas.text(scale(upper), y + 35, f"{upper:.1f}%", cls="small", anchor="middle", fill=color, weight=700)

    canvas.text(60, 582, "Method: 100,000-replicate nonparametric bootstrap over whole task clusters; percentile interval; fixed seed 20260824.", cls="small")
    return write_svg(output_dir, "task-clustered-intervals.svg", canvas)


def build_all(output_dir: Path, *, root: Path = ROOT) -> list[Path]:
    contract = json.loads(
        (root / "reports" / "contract-oracles-v0.1-clustered.json").read_text(
            encoding="utf-8"
        )
    )
    reset = json.loads(
        (root / "reports" / "reset-replication-v0.1-clustered.json").read_text(
            encoding="utf-8"
        )
    )
    return [
        evaluation_contract(output_dir),
        benchmark_oracle_coverage(output_dir),
        task_outcomes(output_dir, contract),
        clustered_intervals(output_dir, reset, contract),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    for path in build_all(args.output_dir):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
