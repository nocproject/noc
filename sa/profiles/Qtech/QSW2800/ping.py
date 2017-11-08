# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Qtech.QSW2800.ping"
    interface = IPing

    rx_stat = re.compile(
        r"Success rate is \d+ percent \((?P<success>\d+)/(?P<count>\d+)\), round-trip min/avg/max = (?P<min>.+)/(?P<avg>.+)/(?P<max>.+) ms",
        re.MULTILINE)

    def execute(self, address, count=None, source_address=None,
                size=None, df=None):
        cmd = "ping"
        cmd += " %s" % address
        ping = self.cli(cmd)
        result = self.rx_stat.search(ping)
        return {
            "success": result.group("success"),
            "count": result.group("count"),
            "min": result.group("min"),
            "avg": result.group("avg"),
            "max": result.group("max"),
        }
