"""Command-line entry point for envcheck."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import compare, scaffold


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envcheck",
        description="Compare a .env file against a .env.example and catch drift.",
    )
    parser.add_argument(
        "--env",
        default=".env",
        help="path to the actual env file (default: .env)",
    )
    parser.add_argument(
        "--example",
        default=".env.example",
        help="path to the reference/example env file (default: .env.example)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="append any keys missing from --env, copying defaults from --example",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    env_path = Path(args.env)
    example_path = Path(args.example)

    if not example_path.exists():
        print(f"envcheck: error: example file not found: {example_path}", file=sys.stderr)
        return 1

    if args.init:
        added = scaffold(env_path, example_path)
        if added:
            print(f"Added {added} missing key(s) to {env_path}.")
        else:
            print(f"{env_path} already has every key from {example_path}.")
        return 0

    result = compare(env_path, example_path)

    if result.is_clean and not result.extra:
        print(f"{env_path} matches {example_path}. Nothing to report.")
        return 0

    if result.missing:
        print(f"Missing from {env_path} ({len(result.missing)}):")
        for key in result.missing:
            print(f"  {key}")

    if result.empty:
        print(f"Empty in {env_path} ({len(result.empty)}):")
        for key in result.empty:
            print(f"  {key}")

    if result.extra:
        print(f"Extra in {env_path}, not in {example_path} ({len(result.extra)}):")
        for key in result.extra:
            print(f"  {key}")

    return 1 if (result.missing or result.empty) else 0


if __name__ == "__main__":
    sys.exit(main())
