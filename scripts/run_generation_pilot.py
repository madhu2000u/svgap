#!/usr/bin/env python3
"""Run a small, explicit model-configuration pilot.

This is an experimental convenience wrapper, not part of the evaluator core.
It disables model tools and evaluates each final response through `svgap pilot`.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASK_ROOT = ROOT / "taskpacks/pilot-v0.1/tasks"
DEFAULT_TASKS = (
    "level_crossing",
    "comb_crossing",
    "gray_counter",
    "reset_release",
    "mode_crossing",
    "alarm_crossing",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", choices=("codex", "claude", "ollama", "command"))
    parser.add_argument("--model", help="provider model name; omit for provider default")
    parser.add_argument("--label", required=True, help="stable configuration label")
    parser.add_argument(
        "--command",
        help=(
            "generation command for the 'command' provider; receives the task "
            "prompt on stdin and must print the model response to stdout"
        ),
    )
    parser.add_argument(
        "--interface-label",
        default="custom-command",
        help="interface identifier recorded in provenance for the 'command' provider",
    )
    parser.add_argument("--task-root", type=Path, default=DEFAULT_TASK_ROOT)
    parser.add_argument("--tasks", nargs="+", default=list(DEFAULT_TASKS))
    parser.add_argument("--samples", type=int, default=1)
    parser.add_argument(
        "--ollama-temperature",
        type=float,
        help="sampling temperature recorded and sent to the Ollama HTTP API",
    )
    parser.add_argument(
        "--ollama-seed-base",
        type=int,
        help="sample N uses seed base + N; omit to leave the seed unspecified",
    )
    parser.add_argument(
        "--codex-reasoning-effort",
        choices=("low", "medium", "high", "xhigh", "max"),
        help="explicit Codex reasoning effort, recorded and passed as configuration",
    )
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="write responses and generation metadata without evaluating RTL",
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "reports/generated/pilot-v0.1"
    )
    args = parser.parse_args()
    output = args.output.resolve()
    if args.samples < 1:
        parser.error("--samples must be positive")
    task_root = args.task_root.resolve()
    if args.provider == "command":
        if not args.command:
            parser.error("the 'command' provider requires --command")
        interface_version = args.interface_label
    else:
        if args.command:
            parser.error("--command is only valid with the 'command' provider")
        if args.provider == "ollama" and not args.model:
            parser.error("the 'ollama' provider requires --model")
        if args.provider != "ollama" and (
            args.ollama_temperature is not None or args.ollama_seed_base is not None
        ):
            parser.error("--ollama-* options require the 'ollama' provider")
        if args.provider != "codex" and args.codex_reasoning_effort is not None:
            parser.error("--codex-reasoning-effort requires the 'codex' provider")
        interface_version = provider_version(args.provider)
    failures = 0
    with tempfile.TemporaryDirectory(prefix="svgap-model-") as sandbox:
        for sample in range(1, args.samples + 1):
            for task_name in args.tasks:
                run_id = f"{args.label}--sample-{sample:02d}"
                response_dir = output / "_responses" / run_id
                response_dir.mkdir(parents=True, exist_ok=True)
                task_dir = task_root / task_name
                prompt = (task_dir / "prompt.md").read_text(encoding="utf-8")
                try:
                    response, command = generate(
                        args.provider,
                        args.model,
                        prompt,
                        Path(sandbox),
                        args.command,
                        sample=sample,
                        ollama_temperature=args.ollama_temperature,
                        ollama_seed_base=args.ollama_seed_base,
                        codex_reasoning_effort=args.codex_reasoning_effort,
                    )
                except (OSError, ValueError, subprocess.SubprocessError) as exc:
                    print(
                        f"GENERATION_ERROR {args.label}/{task_name}: {exc}",
                        file=sys.stderr,
                    )
                    failures += 1
                    continue
                response_path = response_dir / f"{task_name}.txt"
                response_path.write_text(response, encoding="utf-8")
                metadata = {
                    "schema_version": "1.0",
                    "provider": args.provider,
                    "interface_version": interface_version,
                    "requested_model": args.model,
                    "configuration_label": args.label,
                    "sample": sample,
                    "task": task_name,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "command": command,
                }
                if args.provider == "ollama":
                    metadata["generation_options"] = {
                        "temperature": args.ollama_temperature,
                        "seed": (
                            args.ollama_seed_base + sample
                            if args.ollama_seed_base is not None
                            else None
                        ),
                        "stream": False,
                    }
                if args.provider == "codex":
                    metadata["generation_options"] = {
                        "reasoning_effort": args.codex_reasoning_effort,
                    }
                metadata_payload = json.dumps(metadata, indent=2, sort_keys=True) + "\n"
                response_path.with_suffix(".generation.json").write_text(
                    metadata_payload, encoding="utf-8"
                )
                if args.generate_only:
                    print(f"response    {response_path}")
                    continue
                evaluated = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "svgap",
                        "pilot",
                        str(task_dir),
                        str(response_path),
                        "--model",
                        args.model or args.label,
                        "--run-id",
                        run_id,
                        "--output",
                        str(output),
                    ],
                    cwd=ROOT,
                    check=False,
                    text=True,
                )
                if evaluated.returncode == 2:
                    failures += 1
                run_dir = output / run_id / task_name
                if run_dir.is_dir():
                    (run_dir / "generation.json").write_text(
                        metadata_payload, encoding="utf-8"
                    )
    return 2 if failures else 0


def generate(
    provider: str,
    model: str | None,
    prompt: str,
    sandbox: Path,
    command_line: str | None = None,
    *,
    sample: int = 1,
    ollama_temperature: float | None = None,
    ollama_seed_base: int | None = None,
    codex_reasoning_effort: str | None = None,
) -> tuple[str, list[str]]:
    if provider == "command":
        if not command_line:
            raise OSError("the 'command' provider requires a generation command")
        completed = subprocess.run(
            command_line,
            shell=True,
            input=prompt,
            cwd=sandbox,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        if completed.returncode:
            raise subprocess.SubprocessError(completed.stderr[-4000:])
        if not completed.stdout.strip():
            raise subprocess.SubprocessError("generation command produced empty stdout")
        return completed.stdout, [command_line]

    if provider == "ollama":
        if not model:
            raise OSError("the 'ollama' provider requires a model")
        options: dict[str, int | float] = {}
        if ollama_temperature is not None:
            options["temperature"] = ollama_temperature
        if ollama_seed_base is not None:
            options["seed"] = ollama_seed_base + sample
        body: dict[str, object] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if options:
            body["options"] = options
        request = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=600) as response:
            payload = json.loads(response.read())
        text = payload.get("response")
        if not isinstance(text, str) or not text.strip():
            raise subprocess.SubprocessError("Ollama produced an empty response")
        return text, ["ollama-http", "/api/generate", model]

    if provider == "codex":
        binary = require_executable("codex")
        output = sandbox / "last-message.txt"
        command = [
            binary,
            "--ask-for-approval",
            "never",
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--cd",
            str(sandbox),
            "--output-last-message",
            str(output),
        ]
        if codex_reasoning_effort is not None:
            command.extend(
                ["--config", f'model_reasoning_effort="{codex_reasoning_effort}"']
            )
        if model:
            command.extend(["--model", model])
        command.append(prompt)
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=600, check=False
        )
        if completed.returncode:
            raise subprocess.SubprocessError(completed.stderr[-4000:])
        return output.read_text(encoding="utf-8"), redact_command(command)

    binary = require_executable("claude")
    command = [
        binary,
        "--print",
        "--bare",
        "--tools",
        "",
        "--no-session-persistence",
    ]
    if model:
        command.extend(["--model", model])
    command.append(prompt)
    completed = subprocess.run(
        command,
        cwd=sandbox,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    if completed.returncode:
        raise subprocess.SubprocessError(completed.stderr[-4000:])
    return completed.stdout, redact_command(command)


def redact_command(command: list[str]) -> list[str]:
    redacted = command.copy()
    if redacted:
        redacted[-1] = "<PROMPT_FROM_TASKPACK>"
    return redacted


def provider_version(provider: str) -> str:
    if provider == "codex":
        executable = "codex"
    elif provider == "claude":
        executable = "claude"
    elif provider == "ollama":
        executable = "ollama"
    else:
        raise OSError(f"provider has no version command: {provider}")
    binary = require_executable(executable)
    completed = subprocess.run(
        [binary, "--version"], capture_output=True, text=True, timeout=30, check=False
    )
    return (completed.stdout.strip() or completed.stderr.strip() or "unknown").splitlines()[-1]


def require_executable(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise OSError(f"required provider CLI is not on PATH: {name}")
    return path


if __name__ == "__main__":
    raise SystemExit(main())
