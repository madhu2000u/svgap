import subprocess
import sys
import json
import base64
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from scripts.run_generation_pilot import generate


ECHO = f'{sys.executable} -c "import sys; sys.stdout.write(sys.stdin.read())"'
FAIL = f'{sys.executable} -c "import sys; sys.exit(3)"'
EMPTY = f'{sys.executable} -c "pass"'


class CommandProviderTests(TestCase):
    def test_command_receives_prompt_on_stdin_and_returns_stdout(self) -> None:
        with TemporaryDirectory() as sandbox:
            response, command = generate(
                "command", None, "module m; endmodule", Path(sandbox), ECHO
            )
        self.assertEqual(response, "module m; endmodule")
        self.assertEqual(command, [ECHO])

    def test_failing_command_raises(self) -> None:
        with TemporaryDirectory() as sandbox:
            with self.assertRaises(subprocess.SubprocessError):
                generate("command", None, "prompt", Path(sandbox), FAIL)

    def test_empty_stdout_raises(self) -> None:
        with TemporaryDirectory() as sandbox:
            with self.assertRaises(subprocess.SubprocessError):
                generate("command", None, "prompt", Path(sandbox), EMPTY)

    def test_command_provider_requires_command(self) -> None:
        with TemporaryDirectory() as sandbox:
            with self.assertRaises(OSError):
                generate("command", None, "prompt", Path(sandbox), None)

    def test_generate_only_writes_responses_without_reports(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            module = (
                "module reset_config(input logic clk, input logic global_reset_n, "
                "output logic [1:0] config); always_ff @(posedge clk or negedge "
                "global_reset_n) if (!global_reset_n) config <= 0; else config <= "
                "config + 1'b1; endmodule"
            )
            encoded = base64.b64encode(module.encode()).decode()
            command = (
                f'{sys.executable} -c "import base64; '
                f'print(base64.b64decode(\'{encoded}\').decode())"'
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_generation_pilot.py",
                    "command",
                    "--command",
                    command,
                    "--label",
                    "test-model",
                    "--interface-label",
                    "test-harness",
                    "--task-root",
                    "taskpacks/reset-replication-v0.2/tasks",
                    "--tasks",
                    "reset_config",
                    "--samples",
                    "1",
                    "--generate-only",
                    "--output",
                    str(root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            response = root / "_responses/test-model--sample-01/reset_config.txt"
            self.assertTrue(response.is_file())
            self.assertFalse((root / "test-model--sample-01/reset_config/report.json").exists())
            metadata = json.loads(response.with_suffix(".generation.json").read_text())
            self.assertEqual(metadata["interface_version"], "test-harness")

    def test_ollama_provider_sends_recorded_sample_options(self) -> None:
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self) -> bytes:
                return b'{"response":"module m; endmodule"}'

        with TemporaryDirectory() as sandbox, patch(
            "scripts.run_generation_pilot.urllib.request.urlopen",
            return_value=Response(),
        ) as urlopen:
            response, command = generate(
                "ollama",
                "example:1b",
                "prompt",
                Path(sandbox),
                sample=2,
                ollama_temperature=0.2,
                ollama_seed_base=100,
            )
        self.assertEqual(response, "module m; endmodule")
        self.assertEqual(command, ["ollama-http", "/api/generate", "example:1b"])
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(payload["options"], {"seed": 102, "temperature": 0.2})
