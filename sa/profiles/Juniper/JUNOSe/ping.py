# ---------------------------------------------------------------------
# Juniper.JUNOSe.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
from noc.core.validators import is_ipv4


class Script(BaseScript):
    name = "Juniper.JUNOSe.ping"
    interface = IPing
    rx_result = re.compile(
        r"Success rate = \d+% \((?P<success>\d+)/(?P<count>\d+)\), "
        r"round-trip min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+) ms"
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None, vrf=None):
        cmd = "ping"
        if is_ipv4(address):
            cmd += " ip"
        else:
            cmd += " ipv6"
        if vrf:
            cmd += " vrf %s" % vrf
        cmd += " %s" % address
        if count:
            cmd += " %d" % int(count)
        if source_address:
            cmd += " source address %s" % source_address
        if size:
            cmd += " data-size %d" % int(size)
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
