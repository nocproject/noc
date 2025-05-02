# ----------------------------------------------------------------------
# pytest configuration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from typing import DefaultDict
from time import perf_counter_ns

# NOC modules
from noc.tests.fixtures.database import database  # noqa


def pytest_terminal_summary(terminalreporter, exitstatus):
    global _stats
    _stats = terminalreporter.stats


_stats = None

_durations: DefaultDict[str, int] = defaultdict(int)


def pytest_runtest_protocol(item, nextitem):
    global _durations

    start = perf_counter_ns()
    yield  # run the actual test
    duration = perf_counter_ns() - start

    # Get base function name, without parameter suffix
    func_name: str = item.originalname or item.name.split("[")[0]
    _durations[func_name] += duration


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    terminalreporter.write_sep("=", "Test execution time summary")
    total = 0.0
    for func_name, duration in sorted(_durations.items(), key=lambda x: x[1], reverse=True):
        d = float(duration) / 1_000_000_000
        terminalreporter.write_line(f"{func_name:<40} {d:.3f}s")
        total += d
    terminalreporter.write_line(f"Total: {total:.3f}s")
