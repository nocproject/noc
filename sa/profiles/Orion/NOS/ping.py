# ---------------------------------------------------------------------
# Orion.NOS.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "Orion.NOS.ping"
    interface = IPing
    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted,\s*\n"
        r"^(?P<success>\d+) packets received, Success rate is .+\n"
        r"^round-trip \(ms\)  min/avg/max = "
        r"(?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)",
        re.MULTILINE,
    )

    def execute_cli(self, address, count=None, source_address=None, size=None, df=None, vrf=None):
        cmd = "ping %s" % address
        if count:
            cmd += " count %d" % int(count)
        else:
            count = 5
        if size:
            cmd += " size %d" % int(size)
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
        return {"success": 0, "count": count}
