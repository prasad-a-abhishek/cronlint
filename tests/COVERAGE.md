# Test coverage map

Maps each numbered acceptance criterion in `spec.md` to the test(s) that
exercise it. Generated during the build phase to satisfy the contract's
"every spec acceptance criterion has ≥1 test" rule.

Total tests: 134 (plus 11 parametrized realistic-idiom cases).

## 1. Library Interface (spec §1)

| Criterion | Test(s) |
|---|---|
| Function signature `validate_cron(expr, allow_nicknames=True)` | `test_api_returns_tuple_type`, `test_api_accepts_allow_nicknames_kwarg` |
| Returns `(True, None)` when valid | `test_api_returns_true_none_for_valid` |
| Returns `(False, "<error>")` when invalid | `test_api_returns_false_str_for_invalid` |
| Standard 5-field format | `test_5field_basic_all_wildcards`, `test_5field_basic_all_zero`, `test_5field_basic_all_max`, `test_5field_specific_values` |
| Minute field 0-59 | `test_minute_lower_bound_zero`, `test_minute_upper_bound_59`, `test_minute_over_60_invalid`, `test_minute_negative_invalid` |
| Hour field 0-23 | `test_hour_lower_bound_zero`, `test_hour_upper_bound_23`, `test_hour_24_invalid` |
| Day-of-month field 1-31 | `test_dom_lower_bound_1`, `test_dom_upper_bound_31`, `test_dom_zero_invalid`, `test_dom_32_invalid` |
| Month field 1-12 | `test_month_lower_bound_1`, `test_month_upper_bound_12`, `test_month_13_invalid`, `test_month_zero_invalid` |
| Day-of-week field 0-6 | `test_dow_zero_sunday_valid`, `test_dow_six_saturday_valid`, `test_dow_eight_invalid` |
| Day-of-week `7` accepted as Sunday | `test_dow_seven_sunday_valid_per_spec` |
| `*` wildcard | `test_wildcard_each_field`, `test_parse_field_wildcard` |
| `,` lists | `test_list_minute`, `test_parse_field_list` |
| `-` ranges | `test_range_basic`, `test_parse_field_range`, `test_range_inverted_invalid`, `test_range_equal_bounds_invalid` |
| `/` step values | `test_step_basic`, `test_step_with_range`, `test_step_with_start_range`, `test_step_zero_invalid`, `test_step_negative_invalid`, `test_parse_field_step_on_wildcard`, `test_parse_field_step_on_range` |
| Month names `JAN-DEC` case-insensitive | `test_month_name_uppercase`, `test_month_name_lowercase`, `test_month_name_mixed_case`, `test_month_name_range`, `test_month_name_list`, `test_month_name_all_twelve` |
| Day-of-week names `SUN-SAT` case-insensitive | `test_dow_name_uppercase`, `test_dow_name_lowercase`, `test_dow_name_range`, `test_dow_name_list` |
| Nickname `@yearly`/`@annually` | `test_nickname_yearly`, `test_nickname_annually_alias` |
| Nickname `@monthly` | `test_nickname_monthly` |
| Nickname `@weekly` | `test_nickname_weekly` |
| Nickname `@daily`/`@midnight` | `test_nickname_daily`, `test_nickname_midnight_alias` |
| Nickname `@hourly` | `test_nickname_hourly` |
| Nickname `@reboot` | `test_nickname_reboot` |
| Nickname case-insensitivity | `test_nickname_case_insensitive` |

## 2. CLI Interface (spec §2)

| Criterion | Test(s) |
|---|---|
| Command name `cronlint` | `test_cli_help_exits_zero`, `test_cli_main_function_valid` |
| Usage `cronlint "<expression>"` | `test_cli_valid_expression_exits_zero`, `test_cli_invalid_expression_exits_one` |
| Usage `cronlint --file <path>` | `test_cli_file_flag_reads_expression`, `test_cli_file_flag_invalid_expression`, `test_cli_file_missing`, `test_cli_main_function_file` |
| Exit code 0 if valid | `test_cli_valid_expression_exits_zero`, `test_cli_file_flag_reads_expression` |
| Exit code 1 if invalid | `test_cli_invalid_expression_exits_one`, `test_cli_no_nicknames_rejects_nickname` |
| Error details to stderr | `test_cli_invalid_expression_writes_to_stderr`, `test_cli_main_function_invalid` |
| Flag `--no-nicknames` | `test_cli_help_mentions_no_nicknames_flag`, `test_cli_no_nicknames_rejects_nickname`, `test_cli_main_function_no_nicknames`, `test_nickname_disabled_with_flag` |

## 3. Verification & Test Coverage (spec §3)

| Criterion | Test(s) |
|---|---|
| Basic numbers, ranges, lists, steps | `test_5field_specific_values`, `test_range_basic`, `test_list_minute`, `test_step_basic` |
| Complex combinations (`1-10/2,30-40/3`) | `test_complex_combination`, `test_complex_combination_with_invalid_value`, `test_spec_example_complex_combination` |
| Case-insensitive month/day names | `test_month_name_uppercase` / `_lowercase` / `_mixed_case`, `test_dow_name_uppercase` / `_lowercase` |
| Boundary violations (minute 60, day 0) | `test_minute_over_60_invalid`, `test_dom_zero_invalid`, `test_spec_example_boundary_minute_60`, `test_spec_example_boundary_day_0` |
| Malformed formats (4 or 6 fields) | `test_too_few_fields`, `test_too_many_fields`, `test_spec_example_malformed_4_fields`, `test_spec_example_malformed_6_fields` |
| ≥100 test cases | 134 tests collected by pytest |

## Additional categories not in spec but in builder contract's "Proven" pillar

| Category | Coverage |
|---|---|
| Happy path | `test_5field_*`, `test_realistic_idioms` (parametrized, 11 cases) |
| Error paths | `test_minute_over_60_invalid`, `test_hour_24_invalid`, `test_dom_32_invalid`, `test_month_13_invalid`, `test_dow_eight_invalid`, `test_nickname_unknown_invalid`, `test_range_inverted_invalid`, `test_step_zero_invalid`, `test_garbage_text`, `test_pure_letters` |
| Edge cases (empty/null/unicode/garbage) | `test_empty_string`, `test_whitespace_only`, `test_single_field`, `test_unicode_emoji`, `test_unicode_cjk`, `test_partial_garbage`, `test_nickname_prefix_without_value`, `test_nickname_with_invalid_chars` |
| Boundaries | all `*_lower_bound_*` / `*_upper_bound_*` / `*_invalid` field-boundary tests |
| Malformed inputs | `test_too_few_fields`, `test_too_many_fields`, `test_extra_trailing_space`, `test_extra_leading_space`, `test_tabs_as_separator`, `test_multiple_spaces_between_fields` |
| CLI+lib parity | `test_cli_main_function_*` invoke the same `validate_cron` via argparse |
| Regression guards | error-message-name tests (`test_error_message_*`) ensure future refactors don't lose field-specific diagnostics |