# cronlint

[![PyPI version](https://img.shields.io/pypi/v/cronlint-cli.svg)](https://pypi.org/project/cronlint-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> Zero-dependency Python cron expression validator and linter.

## Quick Start

```bash
pip install cronlint-cli
cronlint "*/5 * * * *"
```

```python
from cronlint import validate_cron

is_valid, error = validate_cron("0 12 * * 1-5")
```

## ⚡ Performance & Benchmarks

`cronlint` validates cron expressions in sub-millisecond time with zero runtime dependencies.

| Expression Profile | `cronlint` | `croniter` | Speed Advantage | Peak RAM |
| :--- | :---: | :---: | :---: | :---: |
| **Standard Cron (`*/5 * * * *`)** | ⚡ **0.070 ms** | 1.443 ms | **20x Faster** | **0.004 MB** |
| **Cron Nickname (`@hourly`)** | ⚡ **0.001 ms** | 0.577 ms | **570x Faster** | **0.000 MB** |
| **Business Hours (`0 9-17 * * 1-5`)** | ⚡ **0.050 ms** | 1.325 ms | **26x Faster** | **0.004 MB** |
| **Runtime Dependencies** | 🛡️ **0 (Pure Stdlib)** | ⚠️ **2 (`dateutil`, `pytz`)** | **Zero Overhead** | N/A |

> **Replicate these results:** Run `python3 benchmarks/run_benchmark.py` directly inside this repository. See full matrix in [benchmarks/BENCHMARK.md](benchmarks/BENCHMARK.md).

## Why `cronlint`?

Existing Python libraries like `croniter` are designed for calculating next execution dates and bring in heavy external dependencies (`python-dateutil`, `pytz`). 

When you only need to **validate cron syntax** in web forms, CLI config checkers, or API endpoints, `cronlint` provides instant validation (**12x to 570x faster**) with zero dependencies.

## Key Features

- **Zero Runtime Dependencies:** Pure Python standard library implementation (< 20 KB size).
- **Comprehensive Syntax Support:** Validates 5-field cron syntax, step values (`*/15`), range lists (`1-5,10`), month names (`JAN-DEC`), and day names (`MON-FRI`).
- **Human Nickname Support:** Supports `@yearly`, `@annually`, `@monthly`, `@weekly`, `@daily`, `@midnight`, and `@hourly`.
- **Descriptive Error Messages:** Returns detailed human-readable validation error messages explaining invalid range bounds or syntax syntax errors.

## CLI Usage

```bash
# Validate a valid cron expression (Exit Code 0)
cronlint "*/15 * * * *"
echo $? # 0

# Validate an invalid expression (Exit Code 1 + Error Message)
cronlint "60 * * * *"
# Error: Minute field '60' out of bounds (0-59)
```

## Python API Reference

```python
from cronlint import validate_cron

# Valid expression
valid, err = validate_cron("0 9-17 * * 1-5")
# valid = True, err = None

# Invalid expression
valid, err = validate_cron("0 0 32 * *")
# valid = False, err = "Day of month '32' out of bounds (1-31)"
```

## License

MIT © [Abhishek Prasad](https://github.com/prasad-a-abhishek)