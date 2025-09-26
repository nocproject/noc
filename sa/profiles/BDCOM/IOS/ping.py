# ---------------------------------------------------------------------
# BDCOM.IOS.ping
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
    name = "BDCOM.IOS.ping"
    interface = IPing

    rx_result = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, \d+% packet loss\nround-trip min/avg/max = "
        r"(?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+) ms",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_result1 = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, \d+% packet loss\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    def execute(
        self, address, count=None, source_address=None, size=None, df=None, *args, **kwargs
    ):
        cmd = "ping %s" % address
        if count is not None:
            cmd += " -n %d" % int(count)
        if source_address is not None:
            cmd += " -i %s" % source_address
        if size is not None:
            cmd += " -l %s" % int(size)
        if df is not None:
            cmd += " -f"
        c = self.cli(cmd)
        match = self.rx_result.search(c)
        if match:
            return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"),
            }
        match = self.rx_result1.search(c)
        return {"success": match.group("success"), "count": match.group("count")}
