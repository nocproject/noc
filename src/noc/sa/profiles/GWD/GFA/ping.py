# ---------------------------------------------------------------------
# GWD.GFA.ping
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
    name = "GWD.GFA.ping"
    interface = IPing

    rx_result = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, \d+% packet loss\n\nround-trip\(ms\) min/avg/max = "
        r"(?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    rx_result1 = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, \d+% packet loss\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    def execute_cli(
        self, address, count=None, source_address=None, size=None, df=None, *args, **kwargs
    ):
        cmd = "ping"
        if count is not None:
            cmd += f" -n {int(count)}"
        if source_address is not None:
            cmd += f" -source {source_address}"
        if size is not None:
            cmd += f" -l {int(size)}"
        cmd += f" {address}"
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
