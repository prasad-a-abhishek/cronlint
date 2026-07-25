# Show HN Launch Package: cronlint

**Target Title:**
`Show HN: cronlint – Zero-dependency Python cron expression validator`

**Target URL:**
`https://github.com/prasad-a-abhishek/cronlint`

**Top Comment to Post Immediately After Submission:**

Hi HN! 👋

I built `cronlint` to validate cron expressions in Python without bringing in multi-megabyte timezone and date utility dependencies like `pytz` or `python-dateutil`.

`cronlint` is pure Python (0 runtime dependencies, < 20 KB package size) and supports standard 5-field cron syntax, step values (`*/5`), range lists (`1-5,10`), and human nicknames (`@hourly`, `@daily`).

### ⚡ Benchmark Results (vs. `croniter`)

| Expression Profile | `cronlint` | `croniter` | Speed Advantage |
| :--- | :---: | :---: | :---: |
| **Standard Cron (`*/5 * * * *`)** | ⚡ **0.070 ms** | 1.443 ms | **20x Faster** |
| **Nicknames (`@hourly`)** | ⚡ **0.001 ms** | 0.577 ms | **570x Faster** |
| **Business Hours (`0 9-17 * * 1-5`)** | ⚡ **0.050 ms** | 1.325 ms | **26x Faster** |

### Quick Start
pip install cronlint-cli
cronlint "*/5 * * * *"

Replicate locally: `python3 benchmarks/run_benchmark.py`
GitHub: https://github.com/prasad-a-abhishek/cronlint
PyPI: https://pypi.org/project/cronlint-cli/
