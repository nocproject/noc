# ----------------------------------------------------------------------
# pytest configuration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from typing import DefaultDict, Dict
from time import perf_counter_ns

# NOC modules
from noc.tests.fixtures.database import database  # noqa


def pytest_terminal_summary(terminalreporter, exitstatus):
    global _stats
    _stats = terminalreporter.stats


_stats = None

_durations: DefaultDict[str, int] = defaultdict(int)
_counts: DefaultDict[str, int] = defaultdict(int)
_start_times: Dict[str, int] = {}


def pytest_runtest_setup(item):
    _start_times[item.nodeid] = perf_counter_ns()


def pytest_runtest_teardown(item, nextitem):
    start = _start_times.get(item.nodeid)
    if start is None:
        return
    duration = perf_counter_ns() - start
    # Get base function name, without parameter suffix
    func_name: str = item.originalname or item.name.split("[")[0]
    _durations[func_name] += duration
    _counts[func_name] += 1


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    terminalreporter.write_sep("=", "Test execution time summary")
    total = 0.0
    for func_name, duration in sorted(_durations.items(), key=lambda x: x[1], reverse=True):
        label = func_name
        count = _counts.get(func_name, 0)
        if count > 1:
            label = f"{label} (x{count})"
        d = float(duration) / 1_000_000_000
        terminalreporter.write_line(f"{label:<40} {d:.3f}s")
        total += d
    terminalreporter.write_line(f"Total: {total:.3f}s")
