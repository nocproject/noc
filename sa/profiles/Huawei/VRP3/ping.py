# ---------------------------------------------------------------------
# Huawei.VRP3.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "Huawei.VRP3.ping"
    interface = IPing

    rx_result1 = re.compile(
        r"^\s*Ping statistics for \S+:\s*\n"
        r"^\s*Sent packets\s+: (?P<count>\d+)\s*\n"
        r"^\s*Received packets\s+: (?P<success>\d+)\s*\n"
        r"^\s*.+\n"
        r"^\s*Minimum = (?P<min>\d+)ms, Maximum = (?P<max>\d+)ms, Average = (?P<avg>\d+)ms\s*\n",
        re.MULTILINE | re.DOTALL,
    )
    rx_result2 = re.compile(
        r"^\s*Ping statistics for \S+:\s*\n"
        r"^\s*Sent packets\s+: (?P<count>\d+)\s*\n"
        r"^\s*Received packets\s+: (?P<success>\d+)\s*\n",
        re.MULTILINE,
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = "ping %s" % address
        if count:
            cmd += " -c %d" % int(count)
        else:
            cmd += " -c 3"
            count = 3
        if size:
            cmd += " -s %d" % int(size)
        else:
            cmd += " -s 56"
        cmd += " -t 1000"
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
