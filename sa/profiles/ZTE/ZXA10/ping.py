# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXA10.ping
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
    name = "ZTE.ZXA10.ping"
    interface = IPing
    rx_fail = re.compile(r"Success rate is \d+ percent\((?P<success>\d+)/(?P<count>\d+)\)\.")
    rx_success = re.compile(
        r"Success rate is \d+ percent\((?P<success>\d+)/(?P<count>\d+)\),\s*"
        r"round-trip min/avg/max= (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+) ms\."
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None, vrf=None):
        cmd = "ping %s" % address
        if count:
            cmd += " repaat %d" % int(count)
        if size:
            cmd += " size %d" % int(size)
        if source_address:
            cmd += " source %s" % source_address
        v = self.cli(cmd)
        match = self.rx_success.search(v)
        if match:
            return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"),
            }
        match = self.rx_fail.search(v)
        return {"success": match.group("success"), "count": match.group("count")}
