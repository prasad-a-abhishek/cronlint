"""Top-level validator — implements the public API."""

from __future__ import annotations

from typing import Tuple

from .parser import NICKNAMES, parse_field


def _split_fields(expr: str) -> list[str] | None:
    """Split a 5-field expression. Returns None on wrong field count.

    Uses whitespace as the field separator — the canonical cron format
    documented in crontab(5). Leading/trailing whitespace and runs of
    multiple spaces are tolerated (cron daemons routinely strip these).
    Tab characters are rejected — they are not valid in standard cron.
    """
    if "\t" in expr:
        return None
    parts = expr.split()
    if len(parts) != 5:
        return None
    return parts


def validate_cron(expr: str, allow_nicknames: bool = True) -> Tuple[bool, str | None]:
    """Validate a cron expression.

    Returns (True, None) when expr is a well-formed 5-field cron expression
    (or, when allow_nicknames=True, a recognized nickname like '@daily').
    Returns (False, "<reason>") otherwise. Reasons name the offending field
    so the caller can fix the expression without guesswork.
    """
    if not isinstance(expr, str):
        return False, "expression must be a string"

    stripped = expr.strip()
    if not stripped:
        return False, "empty expression"

    # Nicknames
    if stripped.startswith("@"):
        if not allow_nicknames:
            return False, "nicknames are disabled (--no-nicknames)"
        # Must be exactly @<word>, no trailing punctuation or extra fields.
        body = stripped[1:]
        if not body or not body.isalpha():
            return False, f"invalid nickname {stripped!r}"
        key = body.upper()
        if key not in NICKNAMES:
            return False, f"unknown nickname @{body.lower()}; expected one of: @yearly, @monthly, @weekly, @daily, @hourly, @reboot"
        return True, None

    fields = _split_fields(stripped)
    if fields is None:
        # Distinguish empty from wrong field count for clearer errors.
        if not stripped:
            return False, "empty expression"
        # Detect common malformed shape: too few/many fields.
        n = len([p for p in stripped.split() if p])
        return False, f"expected 5 space-separated fields, got {n}"

    field_names = ("minute", "hour", "dom", "month", "dow")
    for name, value in zip(field_names, fields):
        try:
            parse_field(value, name)
        except ValueError as e:
            return False, f"{name}: {e}"

    return True, None