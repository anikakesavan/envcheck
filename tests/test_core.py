import tempfile
import unittest
from pathlib import Path

from envcheck.core import compare, parse_env_file, scaffold


class TestParseEnvFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, name: str, content: str) -> Path:
        p = self.dir / name
        p.write_text(content)
        return p

    def test_basic_parsing(self):
        p = self.write(".env", "FOO=bar\nBAZ=qux\n")
        self.assertEqual(parse_env_file(p), {"FOO": "bar", "BAZ": "qux"})

    def test_ignores_comments_and_blank_lines(self):
        p = self.write(".env", "# a comment\n\nFOO=bar\n  # indented comment\n")
        self.assertEqual(parse_env_file(p), {"FOO": "bar"})

    def test_strips_export_prefix(self):
        p = self.write(".env", "export FOO=bar\n")
        self.assertEqual(parse_env_file(p), {"FOO": "bar"})

    def test_strips_quotes(self):
        p = self.write(".env", 'FOO="bar"\nBAZ=\'qux\'\n')
        self.assertEqual(parse_env_file(p), {"FOO": "bar", "BAZ": "qux"})

    def test_missing_file_returns_empty_dict(self):
        self.assertEqual(parse_env_file(self.dir / "nope.env"), {})

    def test_skips_malformed_lines(self):
        p = self.write(".env", "not-a-valid-line\nFOO=bar\n")
        self.assertEqual(parse_env_file(p), {"FOO": "bar"})


class TestCompare(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, name: str, content: str) -> Path:
        p = self.dir / name
        p.write_text(content)
        return p

    def test_detects_missing_keys(self):
        env = self.write(".env", "FOO=bar\n")
        example = self.write(".env.example", "FOO=\nBAZ=\n")

        result = compare(env, example)
        self.assertEqual(result.missing, ["BAZ"])
        self.assertEqual(result.extra, [])
        self.assertEqual(result.empty, [])

    def test_detects_extra_keys(self):
        env = self.write(".env", "FOO=bar\nSTALE_KEY=1\n")
        example = self.write(".env.example", "FOO=\n")

        result = compare(env, example)
        self.assertEqual(result.extra, ["STALE_KEY"])

    def test_detects_empty_values(self):
        env = self.write(".env", "FOO=\n")
        example = self.write(".env.example", "FOO=placeholder\n")

        result = compare(env, example)
        self.assertEqual(result.empty, ["FOO"])
        self.assertFalse(result.is_clean)

    def test_matching_files_are_clean(self):
        env = self.write(".env", "FOO=bar\nBAZ=qux\n")
        example = self.write(".env.example", "FOO=\nBAZ=\n")

        result = compare(env, example)
        self.assertTrue(result.is_clean)
        self.assertEqual(result.missing, [])
        self.assertEqual(result.empty, [])


class TestScaffold(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, name: str, content: str) -> Path:
        p = self.dir / name
        p.write_text(content)
        return p

    def test_creates_env_from_example_when_missing(self):
        example = self.write(".env.example", "FOO=default\n")
        env = self.dir / ".env"

        added = scaffold(env, example)
        self.assertEqual(added, 1)
        self.assertEqual(parse_env_file(env), {"FOO": "default"})

    def test_preserves_existing_values(self):
        env = self.write(".env", "FOO=custom\n")
        example = self.write(".env.example", "FOO=default\nBAZ=other\n")

        added = scaffold(env, example)
        self.assertEqual(added, 1)
        self.assertEqual(parse_env_file(env), {"FOO": "custom", "BAZ": "other"})

    def test_no_op_when_already_complete(self):
        env = self.write(".env", "FOO=custom\n")
        example = self.write(".env.example", "FOO=default\n")

        added = scaffold(env, example)
        self.assertEqual(added, 0)
        self.assertEqual(parse_env_file(env), {"FOO": "custom"})


if __name__ == "__main__":
    unittest.main()
