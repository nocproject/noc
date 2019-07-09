# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Polygon.IOS.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Polygon.IOS.ping"
    interface = IPing

    rx_result = re.compile(
        r"Success rate is \d+ percent\((?P<success>\d+)\/(?P<count>\d+)\)"
        r"(,round-trip min\/avg\/max= (?P<min>\d+)\/(?P<avg>\d+)\/(?P<max>\d+) ms)?",
        re.MULTILINE,
    )

    def execute_cli(self, address):
        cmd = "ping %s" % address
        pr = self.cli(cmd)
        match = self.rx_result.search(pr)
        min = match.group("min")
        avg = match.group("avg")
        max = match.group("max")
        r = {"success": match.group("success"), "count": match.group("count")}
        if min and avg and max:
            r["min"] = min
            r["avg"] = avg
            r["max"] = max
        return r
