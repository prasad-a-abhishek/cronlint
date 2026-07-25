"""CLI entry point: `python -m cronlint` and `cronlint` console script."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .validator import validate_cron


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronlint",
        description="Validate cron expressions. Exit 0 if valid, 1 if invalid.",
    )
    p.add_argument(
        "expression",
        nargs="?",
        default=None,
        help="The cron expression to validate (5 space-separated fields or @nickname).",
    )
    p.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Read the expression from this file (whitespace-trimmed).",
    )
    p.add_argument(
        "--no-nicknames",
        action="store_true",
        help="Reject @nickname expressions; only 5-field expressions accepted.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    """Parse args, validate the expression, return the exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.file is None and args.expression is None:
        parser.error("either an expression or --file is required")

    if args.file is not None:
        try:
            text = args.file.read_text()
        except OSError as e:
            print(f"cronlint: cannot read {args.file}: {e}", file=sys.stderr)
            return 2
        expression = text.strip()
    else:
        expression = args.expression

    ok, err = validate_cron(expression, allow_nicknames=not args.no_nicknames)
    if ok:
        return 0

    print(f"cronlint: {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())