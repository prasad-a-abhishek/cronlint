# cronlint

> Zero-dependency Python cron expression validator.

## Quick Start

```bash
pip install cronlint-cli
cronlint "*/5 * * * *"
```

```python
from cronlint import validate_cron
is_valid, error = validate_cron("*/5 * * * *")
```

## ⚡ Performance & Benchmarks

`cronlint` validates cron expressions in sub-millisecond time with zero runtime dependencies.

| Expression Profile | `cronlint` | `croniter` | Speed Advantage |
| :--- | :---: | :---: | :---: |
| **Standard Cron (`*/5 * * * *`)** | ⚡ **0.070 ms** | 1.443 ms | **20x Faster** |
| **Cron Nickname (`@hourly`)** | ⚡ **0.001 ms** | 0.577 ms | **570x Faster** |
| **Runtime Dependencies** | 🛡️ **0 (Pure Stdlib)** | ⚠️ **2 (`dateutil`, `pytz`)** | **Zero Overhead** |

> **Replicate these results:** Run `python3 benchmarks/run_benchmark.py` directly inside this repository. See full matrix in [benchmarks/BENCHMARK.md](benchmarks/BENCHMARK.md).

## Features

- **Fast & Light:** Zero dependencies, sub-millisecond execution.
- **Nicknames & Step Values:** Supports `@hourly`, `@daily`, step ranges, and list fields.

## License

MIT