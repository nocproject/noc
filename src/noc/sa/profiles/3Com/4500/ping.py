# ---------------------------------------------------------------------
# 3Com.4500.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "3Com.4500.ping"
    interface = IPing

    rx_result = re.compile(
        r"\s+(?P<count>\d+) packet\(s\) transmitted.\s+(?P<success>\d+) "
        r"packet\(s\) received.\s+\S+% packet loss.\s+"
        r"round-trip min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+) ms",
        re.DOTALL | re.MULTILINE,
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = "ping -q"
        if df:
            cmd += " -f"
        if count:
            cmd += f" -c {int(count)}"
        if size:
            cmd += f" -s {int(size)}"
        if source_address:
            cmd += f" -a {source_address}"
        cmd += f" {address}"
        ping = self.cli(cmd)
        result = self.rx_result.search(ping)
        return {
            "success": result.group("success"),
            "count": result.group("count"),
            "min": result.group("min"),
            "avg": result.group("avg"),
            "max": result.group("max"),
        }
