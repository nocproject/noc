# ---------------------------------------------------------------------
# VyOS.VyOS.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "VyOS.VyOS.ping"
    interface = IPing

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) received, "
        r"(?:\S+ errors, )?\d+(?:\.\d+)?% packet loss, time \d+ms\nrtt min/avg/max/mdev = "
        r"(?P<min>\d+\.\d+)/(?P<avg>\d+\.\d+)/(?P<max>\d+\.\d+)/\d+\.\d+ ms",
        re.MULTILINE,
    )
    rx_result1 = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>0) received, \S+ errors, "
        r"100% packet loss, time \d+ms\n",
        re.MULTILINE,
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = f"ping {address}"
        if count:
            cmd += f" count {count}"
        else:
            cmd += " count 5"
        if source_address:
            cmd += f" source-address {source_address}"
        if size:
            cmd += f" size {size}"
        if df:
            cmd += " do-not-fragment"
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
