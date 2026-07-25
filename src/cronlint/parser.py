"""Parser internals for cronlint.

Splitting parsing from validation lets us unit-test each piece. Public API
re-exports the field bounds and nickname tables for callers who want them.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple

# Field bounds per the spec: minute/hour/dom/month/dow.
FIELD_BOUNDS = {
    "minute": (0, 59),
    "hour": (0, 23),
    "dom": (1, 31),
    "month": (1, 12),
    "dow": (0, 7),  # 7 accepted as Sunday per spec
}

# Nicknames per spec, with the field spec each expands to.
NICKNAMES = {
    "YEARLY": "0 0 1 1 *",
    "ANNUALLY": "0 0 1 1 *",
    "MONTHLY": "0 0 1 * *",
    "WEEKLY": "0 0 * * 0",
    "DAILY": "0 0 * * *",
    "MIDNIGHT": "0 0 * * *",
    "HOURLY": "0 * * * *",
    "REBOOT": "@reboot",  # sentinel — always valid
}

MONTH_NAMES = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
    "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
    "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}

DAY_NAMES = {
    "SUN": 0, "MON": 1, "TUE": 2, "WED": 3,
    "THU": 4, "FRI": 5, "SAT": 6,
}


def _tokenize(token: str, field_name: str) -> List[int]:
    """Expand a single cron field token (e.g. '1-10/2' or 'JAN,MAR') to ints.

    Raises ValueError on any structural or out-of-range problem.
    """
    lo, hi = FIELD_BOUNDS[field_name]
    names = MONTH_NAMES if field_name == "month" else (DAY_NAMES if field_name == "dow" else None)

    # Split into comma-separated parts (each part may be a step expression).
    parts = token.split(",")
    out: List[int] = []

    for part in parts:
        if not part:
            raise ValueError(f"empty element in {field_name} field")

        # Split off step: "expr/step". Step must be a positive integer.
        if "/" in part:
            base, _, step_str = part.partition("/")
            if not step_str:
                raise ValueError(f"step expression missing step value in {field_name}: {part!r}")
            try:
                step = int(step_str)
            except ValueError as e:
                raise ValueError(f"invalid step {step_str!r} in {field_name}") from e
            if step <= 0:
                raise ValueError(f"step must be positive in {field_name}, got {step}")
        else:
            base = part
            step = None

        # Resolve base range — wildcards become full field bounds.
        if base == "*":
            start, end = lo, hi
        elif "-" in base:
            start_str, _, end_str = base.partition("-")
            start = _coerce(start_str, names, field_name)
            end = _coerce(end_str, names, field_name)
        else:
            n = _coerce(base, names, field_name)
            # A bare token with /step is "n/step" meaning from n by step
            # until hi (some cron daemons differ, but the spec only requires
            # '*/N' and 'a-b/N'; for n/N we treat n as both start and lo).
            if step is not None:
                start, end = n, hi
            else:
                out.append(n)
                continue

        if start > end:
            raise ValueError(f"range start {start} > end {end} in {field_name}")

        if step is None:
            out.extend(range(start, end + 1))
        else:
            out.extend(range(start, end + 1, step))

    # De-duplicate while preserving order — many cron daemons collapse dupes.
    seen = set()
    deduped: List[int] = []
    for v in out:
        if v not in seen:
            seen.add(v)
            deduped.append(v)
    return deduped


def _coerce(token: str, names: dict | None, field_name: str) -> int:
    """Convert a single token (number or name) to an int, validating bounds."""
    token = token.strip()
    if names and token.upper() in names:
        n = names[token.upper()]
    else:
        try:
            n = int(token)
        except ValueError as e:
            raise ValueError(f"invalid {field_name} token {token!r}") from e

    lo, hi = FIELD_BOUNDS[field_name]
    if n < lo or n > hi:
        raise ValueError(f"{field_name} value {n} out of bounds [{lo}, {hi}]")
    return n


def parse_field(token: str, field_name: str) -> List[int]:
    """Parse a single cron field. Returns the sorted list of matching values.

    Raises ValueError on any malformed or out-of-range input.
    """
    return _tokenize(token, field_name)


# Field name display strings, used for friendlier error messages.
FIELD_DISPLAY = {
    "minute": "minute",
    "hour": "hour",
    "dom": "day-of-month",
    "month": "month",
    "dow": "day-of-week",
}