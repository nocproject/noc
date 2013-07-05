# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TracebackPlugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import EventPlugin


class TracebackPlugin(EventPlugin):
    name = "traceback"

    def get_data(self, event, config):
        r = {}
        if "traceback" in event.raw_vars:
            r["traceback"] = event.raw_vars["traceback"]
            r["plugins"] = [
                ("NOC.fm.event.plugins.Traceback", {})
            ]
        return r
