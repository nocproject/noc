# ---------------------------------------------------------------------
# SKS.SKS.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
from noc.core.validators import is_ipv4, is_ipv6


class Script(BaseScript):
    name = "SKS.SKS.ping"
    interface = IPing
    rx_result1 = re.compile(
        r"(?P<count>\d+) packets transmitted, "
        r"(?P<success>\d+) packets received, \d+% packet loss\n"
        r"round-trip( \(ms\))? min/avg/max = "
        r"(?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)",
        re.MULTILINE,
    )
    rx_result2 = re.compile(
        r"(?P<count>\d+) packets transmitted, "
        r"(?P<success>\d+) packets received, \d+% packet loss"
    )

    def execute_cli(self, address, count=None, source_address=None, size=None):
        if is_ipv4(address):
            cmd = "ping ip %s" % address
        elif is_ipv6(address):
            cmd = "ping ipv6 %s" % address
        if count:
            cmd += " count %d" % int(count)
        if size:
            cmd += " size %d" % int(size)
        try:
            s = self.cli(cmd)
        except self.CLISyntaxError:
            if is_ipv4(address):
                cmd = "ping"
            elif is_ipv6(address):
                cmd = "ping6 %s"
            if count:
                cmd += " -n %d" % int(count)
            if size:
                cmd += " -l %d" % int(size)
            cmd = "%s %s" % (cmd, address)
            s = self.cli(cmd)
        match = self.rx_result1.search(s)
        if match:
            return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"),
            }
        match = self.rx_result2.search(s)
        return {"success": match.group("success"), "count": match.group("count")}
