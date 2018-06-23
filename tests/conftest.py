# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# pytest configuration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .fixtures.database import database  # noqa


def pytest_terminal_summary(terminalreporter, exitstatus):
    global _stats
    _stats = terminalreporter.stats


_stats = None
