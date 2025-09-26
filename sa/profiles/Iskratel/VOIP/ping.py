# ---------------------------------------------------------------------
# Iskratel.VOIP.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Iskratel.VOIP.ping"
    interface = IPing

    rx_result = re.compile(
        r"^\s*Packets: Sent = (?P<count>\d+), Received = (?P<success>\d+), "
        r"Lost = \d+%\s*\n"
        r"^\s*Approximate round trip times in milli-seconds:\s*\n"
        r"^\s*Minimum =\s+(?P<min>\d+)ms, Maximum =\s+(?P<max>\d+)ms, "
        r"Average =\s+(?P<avg>\d+)ms",
        re.MULTILINE,
    )

    def execute(
        self, address, count=None, source_address=None, size=None, df=None, *args, **kwargs
    ):
        cmd = "ping %s" % address
        match = self.rx_result.search(self.cli(cmd))
        if match:
            return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"),
            }
        return {"success": 0, "count": 3}
