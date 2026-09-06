import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from envcheck.cli import main


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, name: str, content: str) -> Path:
        p = self.dir / name
        p.write_text(content)
        return p

    def run_cli(self, *args: str) -> tuple[int, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(list(args))
        return code, buf.getvalue()

    def test_reports_missing_keys_and_exits_nonzero(self):
        self.write(".env", "FOO=bar\n")
        self.write(".env.example", "FOO=\nBAZ=\n")

        code, output = self.run_cli(
            "--env", str(self.dir / ".env"),
            "--example", str(self.dir / ".env.example"),
        )
        self.assertEqual(code, 1)
        self.assertIn("Missing from", output)
        self.assertIn("BAZ", output)

    def test_clean_match_exits_zero(self):
        self.write(".env", "FOO=bar\n")
        self.write(".env.example", "FOO=\n")

        code, output = self.run_cli(
            "--env", str(self.dir / ".env"),
            "--example", str(self.dir / ".env.example"),
        )
        self.assertEqual(code, 0)
        self.assertIn("Nothing to report", output)

    def test_missing_example_file_errors(self):
        code, _ = self.run_cli("--example", str(self.dir / "nope.example"))
        self.assertEqual(code, 1)

    def test_init_scaffolds_env(self):
        self.write(".env.example", "FOO=default\n")
        env_path = self.dir / ".env"

        code, output = self.run_cli(
            "--env", str(env_path),
            "--example", str(self.dir / ".env.example"),
            "--init",
        )
        self.assertEqual(code, 0)
        self.assertIn("Added 1 missing key", output)
        self.assertTrue(env_path.exists())


if __name__ == "__main__":
    unittest.main()
