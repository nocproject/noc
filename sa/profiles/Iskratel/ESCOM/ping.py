# ---------------------------------------------------------------------
# Iskratel.ESCOM.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
from noc.core.validators import is_ipv4, is_ipv6
import re


class Script(BaseScript):
    name = "Iskratel.ESCOM.ping"
    interface = IPing
    rx_result1 = re.compile(
        r"(?P<count>\d+) packets transmitted, (?P<success>\d+) packets received, \d+% packet loss\n"
        r"round-trip \(ms\) min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)",
        re.MULTILINE | re.DOTALL,
    )
    rx_result2 = re.compile(
        r"(?P<count>\d+) packets transmitted, (?P<success>\d+) packets received, \d+% packet loss"
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None, vrf=None):
        if is_ipv4(address):
            cmd = "ping ip %s" % address
        elif is_ipv6(address):
            cmd = "ping ipv6 %s" % address
        if count:
            cmd += " count %d" % int(count)
        if size:
            cmd += " size %d" % int(size)
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
