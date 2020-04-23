# ----------------------------------------------------------------------
# pytest configuration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.tests.fixtures.database import database  # noqa


def pytest_terminal_summary(terminalreporter, exitstatus):
    global _stats
    _stats = terminalreporter.stats


_stats = None
