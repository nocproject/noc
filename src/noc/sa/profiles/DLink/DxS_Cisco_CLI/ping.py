# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.ping
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
    name = "DLink.DxS_Cisco_CLI.ping"
    interface = IPing
    rx_result = re.compile(
        r"^Success rate is \d+ percent \((?P<success>\d+)/(?P<count>\d+)\)"
        r"(, round-trip min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)"
        r" ms)?",
        re.MULTILINE | re.DOTALL,
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        if ":" in address:
            cmd = f"ping ipv6 {address}"
            if count:
                cmd += f" -n {int(count)}"
            if source_address:
                cmd += f" -s {source_address}"
            if size:
                cmd += f" -l {int(size)}"
        else:
            cmd = f"ping ip {address}"
            if count:
                cmd += f" ntimes {int(count)}"
            if source_address:
                cmd += f" source {source_address}"
            if size:
                cmd += f" length {int(size)}"
        # Don't implemented, may be in future firmware revisions ?
        # if df:
        #    cmd+=" df-bit"
        match = self.rx_result.search(self.cli(cmd))
        if not match:
            raise self.NotSupportedError()
        return {
            "success": int(match.group("success")),
            "count": int(match.group("count")),
            "min": match.group("min"),
            "avg": match.group("avg"),
            "max": match.group("max"),
        }
