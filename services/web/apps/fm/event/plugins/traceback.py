# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# TracebackPlugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from .base import EventPlugin


class TracebackPlugin(EventPlugin):
    name = "traceback"

    def get_data(self, event, config):
        r = {}
        if "traceback" in event.raw_vars:
            r["traceback"] = event.raw_vars["traceback"]
            r["plugins"] = [("NOC.fm.event.plugins.Traceback", {})]
        return r
