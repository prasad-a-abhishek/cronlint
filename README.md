# cronlint

Validate cron expressions from the CLI or as a Python library.

`cronlint` checks whether a cron expression is well-formed before you commit it
to a crontab or embed it in a deployment. It runs anywhere Python runs — no
system cron daemon required, so it slots cleanly into CI pipelines.

## Why this exists

Cron's grammar is simple but unforgiving: a stray `60` in the minute field or a
typo like `@dailly` will silently never fire. The official way to validate a
cron expression is to install it on a real cron daemon and wait — useless in
CI. Existing validators are mostly JavaScript (`cron-validator`) or tied to a
specific daemon. `cronlint` is the Python option that fits a static check into
your build.

## Install

```bash
pip install git+https://github.com/prasadabhishek/cronlint.git
```

From a clone:

```bash
pip install -e ".[test]"
```

## CLI usage

```bash
cronlint "*/5 * * * *"             # exit 0, valid
cronlint "60 * * * *"              # exit 1, writes error to stderr
cronlint --no-nicknames "@daily"   # exit 1, nicknames disabled
cronlint --file expression.txt     # read expression from file
```

Exit codes: `0` if valid, `1` if invalid, `2` on usage error (missing
arguments or unreadable `--file`).

## Python API

```python
from cronlint import validate_cron

ok, err = validate_cron("*/5 * * * *")
assert ok and err is None

ok, err = validate_cron("60 * * * *")
assert not ok and "minute" in err.lower()
```

The function takes an optional `allow_nicknames` flag (default `True`):

```python
ok, _ = validate_cron("@daily", allow_nicknames=False)
assert not ok
```

### Return shape

`validate_cron` always returns a `tuple[bool, str | None]`:

- `(True, None)` — the expression is well-formed
- `(False, "<reason>")` — the expression is malformed; the string names the
  offending field so the caller can fix the input without guessing

### Exposed constants

| Name           | Purpose                                            |
|----------------|----------------------------------------------------|
| `FIELD_BOUNDS` | `{field: (lo, hi)}` — per-field numeric bounds     |
| `MONTH_NAMES`  | `JAN..DEC -> 1..12` (uppercase keys)               |
| `DAY_NAMES`    | `SUN..SAT -> 0..6` (uppercase keys)                |
| `NICKNAMES`    | nickname -> canonical 5-field expansion            |
| `parse_field`  | expand a single field token to its matching values |

## Supported syntax

Five space-separated fields:

```
[minute] [hour] [day of month] [month] [day of week]
```

| Field           | Range | Names                |
|-----------------|-------|----------------------|
| minute          | 0-59  |                      |
| hour            | 0-23  |                      |
| day of month    | 1-31  |                      |
| month           | 1-12  | `JAN-DEC` (case-insensitive) |
| day of week     | 0-6   | `SUN-SAT` (case-insensitive); `7` is also accepted as Sunday |

Special characters per field:

| Char | Meaning                       | Example     |
|------|-------------------------------|-------------|
| `*`  | any value in range            | `*`         |
| `,`  | list                          | `1,3,5`     |
| `-`  | range (inclusive)             | `1-5`       |
| `/`  | step                          | `*/5`       |
| combination | mix of range + step     | `1-10/2`    |

Nicknames (when not disabled):

| Nickname           | Expands to      |
|--------------------|-----------------|
| `@yearly`          | `0 0 1 1 *`     |
| `@annually`        | `0 0 1 1 *`     |
| `@monthly`         | `0 0 1 * *`     |
| `@weekly`          | `0 0 * * 0`     |
| `@daily`           | `0 0 * * *`     |
| `@midnight`        | `0 0 * * *`     |
| `@hourly`          | `0 * * * *`     |
| `@reboot`          | always valid    |

## Examples

```bash
$ cronlint "*/15 * * * *"
$ echo $?
0

$ cronlint "60 * * * *"
cronlint: minute value 60 out of bounds [0, 59]
$ echo $?
1

$ cronlint "@DAILY"
$ echo $?
0

$ cronlint --no-nicknames "@daily"
cronlint: nicknames are disabled (--no-nicknames)
$ echo $?
1

$ cronlint --file /tmp/job.cron
$ echo $?
0
```

## Limitations

- `cronlint` is a *static* validator. It checks structure and per-field
  ranges; it does not compute the next firing time, and it does not catch
  calendar impossibilities like "Feb 30" (no mainstream cron daemon does
  either).
- `@reboot` is accepted as valid but cannot be statically proven to fire on
  any particular schedule — that requires runtime context.
- Leap-second and timezone-aware validation are out of scope.
- Only single-line expressions are supported; multi-line crontabs are
  iterated line-by-line by the caller (or via `--file`, which trims to the
  first non-empty line).

## Non-goals

- Parsing crontab files with environment-variable assignments, comments, or
  user definitions — only the expression itself is validated.
- Computing firing schedules (`croniter` covers that).
- Daemon-side validation that requires `cron(8)` or `crond(8)`.
- Becoming an LLM wrapper around another library. This is pure stdlib.

## Development

```bash
git clone https://github.com/prasad-a-abhishek/cronlint
cd cronlint
python3 -m venv .venv
.venv/bin/pip install -e ".[test]"
.venv/bin/pytest          # 134 tests
.venv/bin/cronlint "*/5 * * * *"
```

## License

MIT. See `LICENSE`.