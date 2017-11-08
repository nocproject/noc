# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.Comware.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "HP.Comware.ping"
    interface = IPing

    rx_result = re.compile(
        r"^\s+(?P<count>\d+) packet\(s\) transmitted\n"
        r"^\s+(?P<success>\d+) packet\(s\) received\n"
        r"^\s+\S+ packet loss\n"
        r"(^\s+round-trip min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+) ms\n)?",
        re.MULTILINE)

    def execute(self, address, count=None, source_address=None, size=None,
                df=None):
        cmd = "ping"
        if count:
            cmd += " -c %d" % int(count)
        else:
            cmd += " -c 5"
        if source_address:
            cmd += " -a %s" % source_address
        if size:
            cmd += " -s %d" % int(size)
        if df:
            cmd += " -f"
        cmd = "%s %s" % (cmd, address)
        match = self.rx_result.search(self.cli(cmd))
        if not match:
            raise self.NotSupportedError()
        r = {
            "success": int(match.group("success")),
            "count": int(match.group("count")),
        }
        if match.group("min"):
            r["min"] = match.group("min")
            r["avg"] = match.group("avg")
            r["max"] = match.group("max")
        return r
