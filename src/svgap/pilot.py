from __future__ import annotations

import hashlib
import json
import re
import shutil
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from svgap.provenance import canonical_file_set_digest


def load_task(task_dir: Path) -> dict[str, Any]:
    task_dir = task_dir.resolve()
    path = task_dir / "task.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    for key in ("id", "top", "testbench"):
        if key not in data:
            raise ValueError(f"missing {key!r} in {path}")
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", str(data["id"])) is None:
        raise ValueError(f"unsafe task id in {path}: {data['id']!r}")
    testbench = data["testbench"]
    if not isinstance(testbench, str) or not testbench:
        raise ValueError(f"testbench must be a nonempty path in {path}")
    testbench_path = (task_dir / testbench).resolve()
    if not testbench_path.is_file():
        raise ValueError(f"testbench file does not exist: {testbench_path}")
    if "manifest" in data:
        _resolve_task_file(task_dir, data["manifest"], "manifest")
    support_files = data.get("support_files", [])
    if not isinstance(support_files, list) or not all(
        isinstance(item, str) and item for item in support_files
    ):
        raise ValueError(f"support_files must be an array of relative paths in {path}")
    for item in support_files:
        _resolve_task_file(task_dir, item, "support_files")
    prompt_levels = data.get("prompt_levels", {})
    if not isinstance(prompt_levels, dict) or not all(
        isinstance(key, str)
        and key
        and isinstance(value, str)
        and value
        for key, value in prompt_levels.items()
    ):
        raise ValueError(f"prompt_levels must be a string-to-path table in {path}")
    for key, value in prompt_levels.items():
        _resolve_task_file(task_dir, value, f"prompt_levels.{key}")
    default_prompt_level = data.get("default_prompt_level")
    if default_prompt_level is not None and (
        not isinstance(default_prompt_level, str)
        or default_prompt_level not in prompt_levels
    ):
        raise ValueError(
            f"default_prompt_level must name a declared prompt level in {path}"
        )
    return data


def extract_systemverilog(response: str, top: str) -> str:
    fenced = re.findall(r"```(?:systemverilog|verilog|sv)?\s*(.*?)```", response, re.I | re.S)
    candidates = fenced or [response]
    pattern = re.compile(
        rf"\bmodule\s+{re.escape(top)}\b.*?\bendmodule\b", re.S
    )
    for candidate in candidates:
        match = pattern.search(candidate)
        if match:
            return match.group(0).strip() + "\n"
    raise ValueError(f"response does not contain module {top!r}")


def materialize_candidate(
    task_dir: Path,
    response_path: Path,
    model: str,
    output_root: Path,
    run_id: str | None = None,
    *,
    prompt_level: str | None = None,
    prompt_override: str | None = None,
) -> Path:
    task_dir = task_dir.resolve()
    task = load_task(task_dir)
    raw = response_path.read_text(encoding="utf-8")
    design = extract_systemverilog(raw, str(task["top"]))
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", run_id or model).strip("-") or "unknown-model"
    run_dir = output_root.resolve() / slug / str(task["id"])
    run_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(response_path, run_dir / "raw-response.txt")
    (run_dir / "design.sv").write_text(design, encoding="utf-8")
    prompt_path, resolved_prompt_level = resolve_prompt(task_dir, task, prompt_level)
    prompt_payload = (
        prompt_override.encode()
        if prompt_override is not None
        else prompt_path.read_bytes()
    )
    (run_dir / "model-prompt.md").write_bytes(prompt_payload)
    task_path = task_dir / "task.toml"
    testbench_path = (task_dir / str(task["testbench"])).resolve()
    portable_testbench = run_dir / "task-testbench.sv"
    shutil.copy2(testbench_path, portable_testbench)
    for relative in task.get("support_files", []):
        source = _resolve_task_file(task_dir, relative, "support_files")
        target = run_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    evaluator_paths = sorted((Path(__file__).resolve().parent).rglob("*.py"))
    task_inputs = {
        "prompt.md": hashlib.sha256(prompt_payload).hexdigest(),
        "task.toml": hashlib.sha256(task_path.read_bytes()).hexdigest(),
        "testbench": hashlib.sha256(testbench_path.read_bytes()).hexdigest(),
    }
    if "manifest" in task:
        template_path = _resolve_task_file(task_dir, task["manifest"], "manifest")
        task_inputs["manifest"] = hashlib.sha256(template_path.read_bytes()).hexdigest()
    for relative in task.get("support_files", []):
        source = _resolve_task_file(task_dir, relative, "support_files")
        task_inputs[f"support/{relative}"] = hashlib.sha256(source.read_bytes()).hexdigest()
    metadata = {
        "schema_version": "1.0",
        "task_id": task["id"],
        "model": model,
        "run_id": run_id or model,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "prompt_sha256": hashlib.sha256(prompt_payload).hexdigest(),
        "prompt_file": (
            "model-prompt.md"
            if prompt_override is not None
            else str(prompt_path.relative_to(task_dir))
        ),
        "prompt_level": resolved_prompt_level,
        "task_inputs": task_inputs,
        "task_inputs_digest": hashlib.sha256(
            json.dumps(task_inputs, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "evaluator_source_digest": canonical_file_set_digest(
            Path(__file__).resolve().parents[2], evaluator_paths
        ),
        "raw_response_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "design_sha256": hashlib.sha256(design.encode()).hexdigest(),
    }
    manifest_payload = render_manifest(task, task_dir, testbench="task-testbench.sv")
    (run_dir / "manifest.toml").write_text(manifest_payload, encoding="utf-8")
    metadata["manifest_sha256"] = hashlib.sha256(manifest_payload.encode()).hexdigest()
    (run_dir / "provenance.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return run_dir / "manifest.toml"


def resolve_prompt(
    task_dir: Path, task: dict[str, Any], prompt_level: str | None = None
) -> tuple[Path, str | None]:
    """Resolve a model-visible prompt without exposing hidden task support files."""

    task_dir = task_dir.resolve()
    levels = task.get("prompt_levels", {})
    selected = prompt_level
    if selected is None:
        selected = task.get("default_prompt_level")
    if selected is not None:
        if selected not in levels:
            available = ", ".join(sorted(levels)) or "none"
            raise ValueError(
                f"unknown prompt level {selected!r}; available levels: {available}"
            )
        return (
            _resolve_task_file(
                task_dir, levels[selected], f"prompt_levels.{selected}"
            ),
            selected,
        )
    path = (task_dir / "prompt.md").resolve()
    if not path.is_file():
        raise ValueError(f"prompt file does not exist: {path}")
    return path, None


def render_manifest(
    task: dict[str, Any], task_dir: Path, *, testbench: str | Path | None = None
) -> str:
    if "manifest" in task:
        if testbench not in (None, "task-testbench.sv"):
            raise ValueError("manifest-template tasks require task-testbench.sv")
        path = _resolve_task_file(task_dir.resolve(), task["manifest"], "manifest")
        return path.read_text(encoding="utf-8")
    testbench = testbench or (task_dir / str(task["testbench"])).resolve()
    lines = [
        'schema_version = "1.0"',
        f'candidate_id = {toml_string(str(task["id"]))}',
        "[design]",
        f'top = {toml_string(str(task["top"]))}',
        'sources = ["design.sv"]',
        "[functional]",
        "commands = [",
        f'  ["iverilog", "-g2012", "-o", "${{SVGAP_BUILD}}/sim.vvp", "design.sv", {toml_string(str(testbench))}],',
        '  ["vvp", "${SVGAP_BUILD}/sim.vvp"],',
        "]",
        "[structural]",
        'backend = "reference-yosys"',
        "[intent]",
        "asynchronous_groups = " + toml_array(task.get("asynchronous_groups", [])),
    ]
    if "power_on" in task:
        lines.append(f'power_on = {toml_string(str(task["power_on"]))}')
        lines.append(
            "init_attributes_are_power_on = "
            + ("true" if bool(task.get("init_attributes_are_power_on", False)) else "false")
        )
    for clock in task.get("clocks", []):
        lines.extend(
            [
                "[[intent.clocks]]",
                f'name = {toml_string(str(clock["name"]))}',
                f'port = {toml_string(str(clock["port"]))}',
            ]
        )
    for reset in task.get("resets", []):
        lines.extend(["[[intent.resets]]", *[f"{key} = {toml_string(str(reset[key]))}" for key in ("name", "port", "active", "assertion", "deassertion")]])
    for crossing in task.get("crossings", []):
        lines.extend(["[[intent.crossings]]", *[f"{key} = {toml_string(str(crossing[key]))}" for key in ("source", "destination", "protocol")]])
    lines.extend(["[output]", 'report = "report.json"'])
    return "\n".join(lines) + "\n"


def toml_string(value: str) -> str:
    return json.dumps(value)


def toml_array(value: Any) -> str:
    return json.dumps(value)


def _resolve_task_file(task_dir: Path, value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a nonempty relative path")
    relative = Path(value)
    if relative.is_absolute():
        raise ValueError(f"{field} must be a relative path: {value!r}")
    path = (task_dir / relative).resolve()
    if not path.is_relative_to(task_dir):
        raise ValueError(f"{field} escapes the task directory: {value!r}")
    if not path.is_file():
        raise ValueError(f"{field} file does not exist: {path}")
    return path
