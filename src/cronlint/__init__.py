"""cronlint — validate cron expressions from Python or the CLI.

Public API:
    validate_cron(expr: str, allow_nicknames: bool = True) -> tuple[bool, str | None]
"""

from .parser import (
    FIELD_BOUNDS,
    MONTH_NAMES,
    DAY_NAMES,
    NICKNAMES,
    parse_field,
)
from .validator import validate_cron

__all__ = [
    "validate_cron",
    "FIELD_BOUNDS",
    "MONTH_NAMES",
    "DAY_NAMES",
    "NICKNAMES",
    "parse_field",
]

__version__ = "0.1.0"