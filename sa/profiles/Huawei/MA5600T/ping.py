# ---------------------------------------------------------------------
# Huawei.MA5600T.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "Huawei.MA5600T.ping"
    interface = IPing

    rx_result1 = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted\s*\n"
        r"^\s*(?P<success>\d+) packets received\s*\n"
        r"^\s*.+\n"
        r"^\s*round-trip min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+) ms\s*\n",
        re.MULTILINE | re.DOTALL,
    )

    rx_result2 = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted\s*\n"
        r"^\s*(?P<success>\d+) packets received\s*\n",
        re.MULTILINE,
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = "ping"
        if count:
            cmd += " -c %d" % int(count)
        else:
            cmd += " -c 5"
            count = 5
        if size:
            cmd += " -s %d" % int(size)
        cmd += " %s" % address
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
