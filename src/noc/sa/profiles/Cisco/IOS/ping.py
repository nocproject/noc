# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "Cisco.IOS.ping"
    interface = IPing
    rx_result = re.compile(
        r"^Success rate is \d+ percent \((?P<success>\d+)/(?P<count>\d+)\)"
        r"(, round-trip min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)"
        r" ms)?",
        re.MULTILINE | re.DOTALL,
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None, vrf=None):
        cmd = f"ping ip {address}"
        if count:
            cmd += f" count {int(count)}"
        if source_address:
            cmd += f" source {source_address}"
        if size:
            cmd += f" size {int(size)}"
        if df:
            cmd += " df-bit"
        if vrf:
            cmd += f" vrf {vrf}"
        pr = self.cli(cmd)
        match = self.rx_result.search(pr)
        return {
            "success": match.group("success"),
            "count": match.group("count"),
            "min": match.group("min") if match.group("min") else 0.0,
            "avg": match.group("avg") if match.group("avg") else 0.0,
            "max": match.group("max") if match.group("max") else 0.0,
        }
