# ---------------------------------------------------------------------
# Iskratel.MSAN.ping
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
    name = "Iskratel.MSAN.ping"
    interface = IPing

    rx_result = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, \d+% packet loss\nround-trip min/avg/max = "
        r"(?P<min>\d+\.\d+)/(?P<avg>\d+\.\d+)/(?P<max>\d+\.\d+) ms",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_result1 = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, \d+% packet loss\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    def execute(self, address):
        cmd = "ping %s" % address
        s = self.cli(cmd)
        match = self.rx_result.search(s)
        if match:
            return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"),
            }
        match = self.rx_result1.search(s)
        return {"success": match.group("success"), "count": match.group("count")}
