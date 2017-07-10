# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OS.ESXi.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "OS.ESXi.ping"
    interface = IPing
    rx_result = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted, "
        r"(?P<success>\d+) packets received, \d+% packet loss\n"
        r"round-trip min/avg/max = (?P<min>\d+\.\d+)/(?P<avg>\d+\.\d+)/"
        r"(?P<max>\d+\.\d+) ms",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(
        self, address, count=None, source_address=None, size=None, df=None
    ):
        cmd = "ping"
        if count:
            cmd += " -c %d" % int(count)
        else:
            cmd += " -c 5"
        if source_address:
            cmd += " -S %s" % source_address
        if size:
            cmd += " -s %d" % int(size)
        if df:
            cmd += " -D"
        cmd += " %s" % address
        s = self.cli(cmd)
        match = self.rx_result.search(s)
        if match:
            return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max")
            }
        else:
            print "Unknown ping utility"
