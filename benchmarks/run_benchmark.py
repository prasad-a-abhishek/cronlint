import time, sys, statistics, os
from croniter import croniter
sys.path.insert(0, os.path.abspath("../src"))
from cronlint import validate_cron

expr = "*/5 * * * *"
cl_times, cr_times = [], []
for _ in range(50):
    t0 = time.perf_counter()
    r = validate_cron(expr)
    cl_times.append((time.perf_counter() - t0)*1000)
    
    t0 = time.perf_counter()
    r = croniter.is_valid(expr)
    cr_times.append((time.perf_counter() - t0)*1000)

print(f"cronlint: {statistics.mean(cl_times):.4f} ms | croniter: {statistics.mean(cr_times):.4f} ms")
