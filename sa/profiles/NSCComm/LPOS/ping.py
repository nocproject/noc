# ---------------------------------------------------------------------
# NSCComm.LPOS.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "NSCComm.LPOS.ping"
    interface = IPing

    rx_result = re.compile(
        r"^\s*Packets: Sent (?P<count>\d+), Received (?P<success>\d+), Lost.+\n"
        r"^Approximate round trip times:\s*\n"
        r"^\s*Minimum (?P<min>\S+)ms, Maximum (?P<max>\S+)ms, Average (?P<avg>\S+)ms",
        re.MULTILINE,
    )
    rx_result1 = re.compile(
        r"^\s*Packets: Sent (?P<count>\d+), Received (?P<success>\d+), Lost", re.MULTILINE
    )

    def execute(
        self, address, count=None, source_address=None, size=None, df=None, *args, **kwargs
    ):
        if not count:
            count = 3
        cmd = "ping -t %d %s " % (int(count), address)
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
