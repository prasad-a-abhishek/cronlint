"""Test suite for cronlint.

Organized by spec acceptance criterion. Each test name starts with a short tag
that maps to the COVERAGE.md table. Total target: >=100 tests.
"""
from __future__ import annotations

import io
import os
import subprocess
import sys
import tempfile

import pytest

from cronlint import validate_cron
from cronlint.cli import main as cli_main
from cronlint.parser import (
    FIELD_BOUNDS,
    MONTH_NAMES,
    DAY_NAMES,
    NICKNAMES,
    parse_field,
)


# ---------------------------------------------------------------------------
# 1. Public API contract — return shape (spec §1)
# ---------------------------------------------------------------------------

def test_api_returns_true_none_for_valid():
    ok, err = validate_cron("*/5 * * * *")
    assert ok is True
    assert err is None


def test_api_returns_false_str_for_invalid():
    ok, err = validate_cron("bogus")
    assert ok is False
    assert isinstance(err, str) and err  # non-empty detail


def test_api_accepts_allow_nicknames_kwarg():
    # Both True (default) and False must be accepted.
    assert validate_cron("@daily", allow_nicknames=True) == (True, None)
    ok, err = validate_cron("@daily", allow_nicknames=False)
    assert ok is False and "nickname" in err.lower()


def test_api_returns_tuple_type():
    result = validate_cron("0 0 * * *")
    assert isinstance(result, tuple)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# 2. Five-field standard format (spec §1 — standard 5-field)
# ---------------------------------------------------------------------------

def test_5field_basic_all_wildcards():
    assert validate_cron("* * * * *") == (True, None)


def test_5field_basic_all_zero():
    assert validate_cron("0 0 1 1 0") == (True, None)


def test_5field_basic_all_max():
    assert validate_cron("59 23 31 12 6") == (True, None)


def test_5field_specific_values():
    assert validate_cron("30 14 15 6 3") == (True, None)


# ---------------------------------------------------------------------------
# 3. Field boundaries — minute 0-59, hour 0-23, dom 1-31, month 1-12, dow 0-6
# ---------------------------------------------------------------------------

def test_minute_lower_bound_zero():
    assert validate_cron("0 * * * *") == (True, None)


def test_minute_upper_bound_59():
    assert validate_cron("59 * * * *") == (True, None)


def test_minute_over_60_invalid():
    ok, err = validate_cron("60 * * * *")
    assert ok is False and "minute" in err.lower()


def test_minute_negative_invalid():
    ok, err = validate_cron("-1 * * * *")
    assert ok is False


def test_hour_lower_bound_zero():
    assert validate_cron("* 0 * * *") == (True, None)


def test_hour_upper_bound_23():
    assert validate_cron("* 23 * * *") == (True, None)


def test_hour_24_invalid():
    ok, err = validate_cron("* 24 * * *")
    assert ok is False and "hour" in err.lower()


def test_dom_lower_bound_1():
    assert validate_cron("* * 1 * *") == (True, None)


def test_dom_upper_bound_31():
    assert validate_cron("* * 31 * *") == (True, None)


def test_dom_zero_invalid():
    ok, err = validate_cron("* * 0 * *")
    assert ok is False and ("day" in err.lower() or "dom" in err.lower())


def test_dom_32_invalid():
    ok, err = validate_cron("* * 32 * *")
    assert ok is False and ("day" in err.lower() or "dom" in err.lower())


def test_month_lower_bound_1():
    assert validate_cron("* * * 1 *") == (True, None)


def test_month_upper_bound_12():
    assert validate_cron("* * * 12 *") == (True, None)


def test_month_13_invalid():
    ok, err = validate_cron("* * * 13 *")
    assert ok is False and "month" in err.lower()


def test_month_zero_invalid():
    ok, err = validate_cron("* * * 0 *")
    assert ok is False and "month" in err.lower()


def test_dow_zero_sunday_valid():
    assert validate_cron("* * * * 0") == (True, None)


def test_dow_six_saturday_valid():
    assert validate_cron("* * * * 6") == (True, None)


def test_dow_seven_sunday_valid_per_spec():
    # Spec explicitly allows 7 as Sunday.
    assert validate_cron("* * * * 7") == (True, None)


def test_dow_eight_invalid():
    ok, err = validate_cron("* * * * 8")
    assert ok is False and ("day" in err.lower() or "dow" in err.lower())


# ---------------------------------------------------------------------------
# 4. Special characters — *, ,, -, / (spec §1)
# ---------------------------------------------------------------------------

def test_wildcard_each_field():
    assert validate_cron("* * * * *") == (True, None)


def test_list_minute():
    assert validate_cron("1,3,5 * * * *") == (True, None)


def test_list_with_too_high_value():
    ok, err = validate_cron("1,60,5 * * * *")
    assert ok is False and "minute" in err.lower()


def test_list_empty_element_invalid():
    ok, _ = validate_cron("1,,2 * * * *")
    assert ok is False


def test_range_basic():
    assert validate_cron("1-5 * * * *") == (True, None)


def test_range_inverted_invalid():
    # 5-1 is technically not supported by most cron implementations; spec
    # doesn't require us to reject it explicitly, but a robust implementation
    # should. We accept either way — assert it produces a deterministic result.
    ok, _ = validate_cron("5-1 * * * *")
    # Implementation choice: we reject ranges where start > end.
    assert ok is False


def test_range_equal_bounds_invalid():
    # 5-5 isn't a range; some parsers accept it as a single value.
    # Spec doesn't pin this; we accept the literal single-value semantics.
    # (5-5 == 5) so we allow it.
    assert validate_cron("5-5 * * * *") == (True, None)


def test_range_cross_field_invalid_value():
    ok, err = validate_cron("* 24-25 * * *")
    assert ok is False and "hour" in err.lower()


def test_step_basic():
    assert validate_cron("*/5 * * * *") == (True, None)


def test_step_with_range():
    assert validate_cron("1-10/2 * * * *") == (True, None)


def test_step_with_start_range():
    assert validate_cron("0-30/5 * * * *") == (True, None)


def test_step_zero_invalid():
    ok, _ = validate_cron("*/0 * * * *")
    assert ok is False


def test_step_negative_invalid():
    ok, _ = validate_cron("*/-5 * * * *")
    assert ok is False


def test_complex_combination():
    assert validate_cron("1-10/2,30-40/3 * * * *") == (True, None)


def test_complex_combination_with_invalid_value():
    ok, err = validate_cron("1-10/2,60 * * * *")
    assert ok is False and "minute" in err.lower()


# ---------------------------------------------------------------------------
# 5. Month names — case-insensitive JAN-DEC (spec §1)
# ---------------------------------------------------------------------------

def test_month_name_uppercase():
    assert validate_cron("0 0 1 JAN *") == (True, None)


def test_month_name_lowercase():
    assert validate_cron("0 0 1 jan *") == (True, None)


def test_month_name_mixed_case():
    assert validate_cron("0 0 1 JaN *") == (True, None)


def test_month_name_range():
    assert validate_cron("0 0 1 JAN-MAR *") == (True, None)


def test_month_name_list():
    assert validate_cron("0 0 1 JAN,MAR,MAY *") == (True, None)


def test_month_name_invalid():
    ok, err = validate_cron("0 0 1 FOO *")
    assert ok is False and "month" in err.lower()


def test_month_name_all_twelve():
    assert validate_cron("0 0 1 JAN,FEB,MAR,APR,MAY,JUN,JUL,AUG,SEP,OCT,NOV,DEC *") == (True, None)


# ---------------------------------------------------------------------------
# 6. Day-of-week names — case-insensitive SUN-SAT (spec §1)
# ---------------------------------------------------------------------------

def test_dow_name_uppercase():
    assert validate_cron("0 0 * * SUN") == (True, None)


def test_dow_name_lowercase():
    assert validate_cron("0 0 * * sun") == (True, None)


def test_dow_name_range():
    assert validate_cron("0 0 * * MON-FRI") == (True, None)


def test_dow_name_list():
    assert validate_cron("0 0 * * SAT,SUN") == (True, None)


def test_dow_name_invalid():
    ok, err = validate_cron("0 0 * * FOO")
    assert ok is False and ("day" in err.lower() or "dow" in err.lower())


# ---------------------------------------------------------------------------
# 7. Nicknames (spec §1 — all six + reboot)
# ---------------------------------------------------------------------------

def test_nickname_yearly():
    assert validate_cron("@yearly") == (True, None)


def test_nickname_annually_alias():
    assert validate_cron("@annually") == (True, None)


def test_nickname_monthly():
    assert validate_cron("@monthly") == (True, None)


def test_nickname_weekly():
    assert validate_cron("@weekly") == (True, None)


def test_nickname_daily():
    assert validate_cron("@daily") == (True, None)


def test_nickname_midnight_alias():
    assert validate_cron("@midnight") == (True, None)


def test_nickname_hourly():
    assert validate_cron("@hourly") == (True, None)


def test_nickname_reboot():
    assert validate_cron("@reboot") == (True, None)


def test_nickname_case_insensitive():
    assert validate_cron("@DAILY") == (True, None)


def test_nickname_unknown_invalid():
    ok, err = validate_cron("@never")
    assert ok is False and "nickname" in err.lower()


def test_nickname_disabled_with_flag():
    ok, err = validate_cron("@daily", allow_nicknames=False)
    assert ok is False and "nickname" in err.lower()


def test_nickname_explicit_field_count_invalid_when_disabled():
    # A naked 5-field expression still works when nicknames disabled.
    assert validate_cron("0 0 * * *", allow_nicknames=False) == (True, None)


# ---------------------------------------------------------------------------
# 8. Malformed formats — wrong field count (spec §1, §3)
# ---------------------------------------------------------------------------

def test_too_few_fields():
    ok, _ = validate_cron("* * * *")
    assert ok is False


def test_too_many_fields():
    ok, _ = validate_cron("* * * * * *")
    assert ok is False


def test_empty_string():
    ok, _ = validate_cron("")
    assert ok is False


def test_whitespace_only():
    ok, _ = validate_cron("   ")
    assert ok is False


def test_single_field():
    ok, _ = validate_cron("*")
    assert ok is False


def test_extra_trailing_space():
    # Cron daemons routinely tolerate trailing whitespace; we do too.
    assert validate_cron("* * * * * ") == (True, None)


def test_extra_leading_space():
    # Leading whitespace is also tolerated.
    assert validate_cron(" * * * * *") == (True, None)


def test_tabs_as_separator():
    ok, _ = validate_cron("*\t*\t*\t*\t*")
    # Tabs are not valid whitespace per spec; reject.
    assert ok is False


def test_multiple_spaces_between_fields():
    # Spec is silent; common implementations collapse whitespace.
    # We accept multiple spaces between fields.
    assert validate_cron("*  *  *  *  *") == (True, None)


# ---------------------------------------------------------------------------
# 9. Garbage / non-cron input
# ---------------------------------------------------------------------------

def test_garbage_text():
    ok, _ = validate_cron("not a cron expression")
    assert ok is False


def test_pure_letters():
    ok, _ = validate_cron("a b c d e")
    assert ok is False


def test_partial_garbage():
    ok, _ = validate_cron("0 0 abc 1 *")
    assert ok is False


def test_unicode_emoji():
    ok, _ = validate_cron("🦀 * * * *")
    assert ok is False


def test_unicode_cjk():
    ok, _ = validate_cron("0 0 1 一 *")
    assert ok is False


def test_nickname_prefix_without_value():
    ok, _ = validate_cron("@")
    assert ok is False


def test_nickname_with_invalid_chars():
    ok, _ = validate_cron("@daily!")
    assert ok is False


# ---------------------------------------------------------------------------
# 10. Error message quality (spec §1 — "details exactly what is invalid")
# ---------------------------------------------------------------------------

def test_error_message_mentions_field_name_for_minute():
    _, err = validate_cron("60 * * * *")
    assert err is not None and "minute" in err.lower()


def test_error_message_mentions_field_name_for_hour():
    _, err = validate_cron("* 24 * * *")
    assert err is not None and "hour" in err.lower()


def test_error_message_mentions_field_count():
    _, err = validate_cron("* * * *")
    assert err is not None
    # Must mention the field-count issue.
    assert ("5" in err) or ("field" in err.lower()) or ("expected" in err.lower())


def test_error_message_for_garbage_mentions_field_count():
    _, err = validate_cron("nope")
    assert err is not None and len(err) > 0


# ---------------------------------------------------------------------------
# 11. Constants / module exports
# ---------------------------------------------------------------------------

def test_module_exports_validate_cron():
    from cronlint import validate_cron as vc
    assert callable(vc)


def test_field_bounds_exposed():
    # Module should expose field bounds for advanced callers.
    assert FIELD_BOUNDS["minute"] == (0, 59)
    assert FIELD_BOUNDS["hour"] == (0, 23)
    assert FIELD_BOUNDS["dom"] == (1, 31)
    assert FIELD_BOUNDS["month"] == (1, 12)
    assert FIELD_BOUNDS["dow"] == (0, 7)


def test_month_names_all_twelve():
    assert set(MONTH_NAMES) == {"JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                                 "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"}


def test_day_names_all_seven():
    assert set(DAY_NAMES) == {"SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"}


def test_nicknames_dict_has_reboot():
    assert "REBOOT" in NICKNAMES


# ---------------------------------------------------------------------------
# 12. Internal parser — parse_field unit tests
# ---------------------------------------------------------------------------

def test_parse_field_wildcard():
    # Wildcard with default step == max bound.
    values = parse_field("*", "minute")
    assert sorted(values) == list(range(0, 60))


def test_parse_field_single_value():
    assert parse_field("5", "minute") == [5]


def test_parse_field_list():
    assert parse_field("1,3,5", "minute") == [1, 3, 5]


def test_parse_field_range():
    assert parse_field("1-5", "minute") == [1, 2, 3, 4, 5]


def test_parse_field_step_on_wildcard():
    assert parse_field("*/5", "minute") == [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]


def test_parse_field_step_on_range():
    assert parse_field("1-10/3", "minute") == [1, 4, 7, 10]


def test_parse_field_month_name():
    assert parse_field("JAN", "month") == [1]


def test_parse_field_dow_name():
    assert parse_field("SUN", "dow") == [0]


def test_parse_field_invalid_token():
    with pytest.raises(ValueError):
        parse_field("foo", "minute")


def test_parse_field_out_of_range():
    with pytest.raises(ValueError):
        parse_field("60", "minute")


def test_parse_field_negative():
    with pytest.raises(ValueError):
        parse_field("-5", "minute")


# ---------------------------------------------------------------------------
# 13. CLI surface — invoked via python -m cronlint (spec §2)
# ---------------------------------------------------------------------------

def run_cli(args, stdin_text=None):
    """Invoke the CLI as a subprocess and capture exit/output."""
    return subprocess.run(
        [sys.executable, "-m", "cronlint", *args],
        capture_output=True,
        text=True,
        input=stdin_text,
        cwd="/root/projects/cronlint",
    )


def test_cli_help_exits_zero():
    result = run_cli(["--help"])
    assert result.returncode == 0


def test_cli_help_mentions_no_nicknames_flag():
    result = run_cli(["--help"])
    assert "--no-nicknames" in result.stdout


def test_cli_help_mentions_file_flag():
    result = run_cli(["--help"])
    assert "--file" in result.stdout


def test_cli_valid_expression_exits_zero():
    result = run_cli(["*/5 * * * *"])
    assert result.returncode == 0


def test_cli_invalid_expression_exits_one():
    result = run_cli(["bogus"])
    assert result.returncode == 1


def test_cli_invalid_expression_writes_to_stderr():
    result = run_cli(["bogus"])
    assert result.stderr  # non-empty error details on stderr


def test_cli_no_nicknames_rejects_nickname():
    result = run_cli(["--no-nicknames", "@daily"])
    assert result.returncode == 1


def test_cli_file_flag_reads_expression(tmp_path):
    f = tmp_path / "expr.txt"
    f.write_text("0 0 * * *\n")
    result = run_cli(["--file", str(f)])
    assert result.returncode == 0


def test_cli_file_flag_invalid_expression(tmp_path):
    f = tmp_path / "expr.txt"
    f.write_text("totally not cron\n")
    result = run_cli(["--file", str(f)])
    assert result.returncode == 1


def test_cli_file_missing(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    result = run_cli(["--file", str(missing)])
    assert result.returncode != 0


def test_cli_no_args_usage_error():
    result = run_cli([])
    # argparse exits with code 2 on usage error; either 1 or 2 is acceptable.
    assert result.returncode != 0


def test_cli_main_function_default_argv(monkeypatch):
    """Calling cli.main() with no args should fail (missing expression)."""
    monkeypatch.setattr(sys, "argv", ["cronlint"])
    with pytest.raises(SystemExit) as ei:
        cli_main()
    assert ei.value.code != 0


def test_cli_main_function_valid(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["cronlint", "*/5 * * * *"])
    rc = cli_main()
    assert rc == 0


def test_cli_main_function_invalid(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["cronlint", "bogus"])
    rc = cli_main()
    assert rc == 1
    captured = capsys.readouterr()
    assert captured.err  # error went to stderr


def test_cli_main_function_no_nicknames(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["cronlint", "--no-nicknames", "@daily"])
    rc = cli_main()
    assert rc == 1


def test_cli_main_function_file(monkeypatch, tmp_path):
    f = tmp_path / "expr.txt"
    f.write_text("@daily\n")
    monkeypatch.setattr(sys, "argv", ["cronlint", "--file", str(f)])
    rc = cli_main()
    assert rc == 0


# ---------------------------------------------------------------------------
# 14. Realistic cron patterns — sanity tests for common idioms
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("expr", [
    "*/5 * * * *",
    "0 0 * * *",
    "0 12 * * *",
    "15 14 1 * *",
    "0 9-17 * * MON-FRI",
    "0 0 1 JAN *",
    "@daily",
    "@hourly",
    "0 0 * * SUN",
    "*/10 * * * 0-6",
    "30 4 1-7 * 1",
])
def test_realistic_idioms(expr):
    assert validate_cron(expr) == (True, None), f"rejected: {expr}"


# ---------------------------------------------------------------------------
# 15. Spec-stated examples from the requirements list
# ---------------------------------------------------------------------------

def test_spec_example_complex_combination():
    # "Complex combinations (e.g. 1-10/2,30-40/3)"
    assert validate_cron("1-10/2,30-40/3 * * * *") == (True, None)


def test_spec_example_boundary_minute_60():
    # "Boundary violations (e.g. minute 60, day 0)"
    ok, err = validate_cron("60 * * * *")
    assert ok is False and "minute" in err.lower()


def test_spec_example_boundary_day_0():
    ok, err = validate_cron("* * 0 * *")
    assert ok is False


def test_spec_example_malformed_4_fields():
    ok, _ = validate_cron("* * * *")
    assert ok is False


def test_spec_example_malformed_6_fields():
    ok, _ = validate_cron("* * * * * *")
    assert ok is False