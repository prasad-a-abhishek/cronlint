# Changelog

All notable changes to `cronlint` are documented here.

## 0.1.0 — 2026-07-25 — initial release

- Public API `validate_cron(expr, allow_nicknames=True)` returning `(bool, str | None)`
- CLI `cronlint` with `--file` and `--no-nicknames` flags, exit codes 0/1/2
- Support for all 5 standard fields with bounds, lists, ranges, and steps
- Case-insensitive `JAN-DEC` month names and `SUN-SAT` day-of-week names
- `7` accepted as Sunday for day-of-week (common-convention extension)
- All eight nicknames: `@yearly`, `@annually`, `@monthly`, `@weekly`,
  `@daily`, `@midnight`, `@hourly`, `@reboot`
- 134 tests covering every spec acceptance criterion plus extensive
  fuzz-style inputs (empty, garbage, unicode, malformed field counts)
- Zero runtime dependencies; test dep is `pytest`