# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Force10.FTOS.ping"
    interface = IPing
    rx_result = re.compile(r"^Success rate is \d+(?:\.\d+) percent \((?P<success>\d+)/(?P<count>\d+)\)(, round-trip min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+) \(ms\))?", re.MULTILINE | re.DOTALL)

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = "ping %s" % address
        pr = self.cli(cmd)
        match = self.re_search(self.rx_result, pr)
        return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"),
        }
