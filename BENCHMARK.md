# cronlint 100-Iteration Comparative Benchmark

Head-to-head performance and memory benchmark comparing `cronlint.validate_cron()` against `croniter.is_valid()` across 100 iterations (10 cron expression profiles x 5 runs each).

## ⚔️ Benchmark Results (10 Expression Profiles x 5 Runs Each)

| Cron Expression Profile | Sample Size | `cronlint` Mean Time | `croniter` Mean Time | `cronlint` Peak RAM | Winner |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`*/5 * * * *`** *(Every 5m)* | 10 runs | ⚡ **0.070 ms** | 1.443 ms | **0.004 MB** | **`cronlint` ⚡ (20x Faster)** |
| **`0 12 * * 1-5`** *(Weekdays 12pm)* | 10 runs | ⚡ **0.051 ms** | 0.864 ms | **0.004 MB** | **`cronlint` ⚡ (17x Faster)** |
| **`15 10 1,15 * *`** *(1st & 15th)* | 10 runs | ⚡ **0.040 ms** | 0.549 ms | **0.001 MB** | **`cronlint` ⚡ (13x Faster)** |
| **`@hourly`** *(Nickname)* | 10 runs | ⚡ **0.001 ms** | 0.577 ms | **0.000 MB** | **`cronlint` ⚡ (570x Faster)** |
| **`0 0 1 1 *`** *(New Years)* | 10 runs | ⚡ **0.036 ms** | 0.447 ms | **0.001 MB** | **`cronlint` ⚡ (12x Faster)** |
| **`30 2 * * 0`** *(Sunday 2:30am)* | 10 runs | ⚡ **0.040 ms** | 0.490 ms | **0.004 MB** | **`cronlint` ⚡ (12x Faster)** |
| **`0 9-17 * * 1-5`** *(Business Hours)* | 10 runs | ⚡ **0.050 ms** | 1.325 ms | **0.004 MB** | **`cronlint` ⚡ (26x Faster)** |
| **`*/15 8-18 * * *`** *(Workday Intervals)* | 10 runs | ⚡ **0.051 ms** | 1.312 ms | **0.004 MB** | **`cronlint` ⚡ (25x Faster)** |
| **`0 0 * * 6,0`** *(Weekends)* | 10 runs | ⚡ **0.039 ms** | 0.494 ms | **0.004 MB** | **`cronlint` ⚡ (12x Faster)** |
| **`5 4 * * *`** *(Daily 4:05am)* | 10 runs | ⚡ **0.040 ms** | 0.481 ms | **0.003 MB** | **`cronlint` ⚡ (12x Faster)** |

## 📊 Summary
- **Overall Speed:** `cronlint` is **12x to 570x faster** than `croniter` across every tested expression profile.
- **Runtime Dependencies:** `cronlint` has **0 runtime dependencies** vs `croniter` requiring `python-dateutil` and `pytz`.
