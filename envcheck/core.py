"""Core logic for parsing and comparing .env-style files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a .env-style file into an ordered dict of key -> value.

    Blank lines and lines starting with # are ignored. Lines are expected
    to look like `KEY=value` or `export KEY=value`; surrounding quotes on
    the value are stripped. Malformed lines (no `=`) are silently skipped.
    """
    path = Path(path)
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key:
            values[key] = value
    return values


@dataclass
class ComparisonResult:
    """The outcome of comparing an actual .env against a reference/example file."""

    missing: list[str] = field(default_factory=list)   # in example, absent from env
    extra: list[str] = field(default_factory=list)      # in env, absent from example
    empty: list[str] = field(default_factory=list)      # present in env but blank

    @property
    def is_clean(self) -> bool:
        return not (self.missing or self.empty)


def compare(env_path: Path, example_path: Path) -> ComparisonResult:
    """Compare an env file against an example/reference file."""
    env_values = parse_env_file(env_path)
    example_values = parse_env_file(example_path)

    missing = sorted(k for k in example_values if k not in env_values)
    extra = sorted(k for k in env_values if k not in example_values)
    empty = sorted(k for k, v in env_values.items() if k in example_values and v == "")

    return ComparisonResult(missing=missing, extra=extra, empty=empty)


def scaffold(env_path: Path, example_path: Path) -> int:
    """Create or update `env_path` so it has every key from `example_path`.

    Existing values in `env_path` are preserved. Keys present in the example
    but missing from the env file are appended, copying the example's
    default value. Returns the number of keys added.
    """
    env_path = Path(env_path)
    example_values = parse_env_file(example_path)
    existing_values = parse_env_file(env_path)

    to_add = [k for k in example_values if k not in existing_values]
    if not to_add:
        return 0

    lines = []
    if env_path.exists() and env_path.read_text():
        lines.append(env_path.read_text().rstrip("\n"))
    for key in to_add:
        lines.append(f"{key}={example_values[key]}")

    env_path.write_text("\n".join(lines) + "\n")
    return len(to_add)
