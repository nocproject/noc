# ---------------------------------------------------------------------
# Iskratel.MBAN.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Iskratel.MBAN.ping"
    interface = IPing

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, \d+% packet loss\s*\nround-trip \(ms\)\s+min/avg/max = "
        r"(?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)",
        re.MULTILINE,
    )

    def execute(
        self, address, count=None, source_address=None, size=None, df=None, *args, **kwargs
    ):
        cmd = "show ping %s" % address
        if count is not None:
            cmd += " number %s" % count
        else:
            count = 3
        if size is not None:
            cmd += " packetsize %s" % size
        match = self.rx_result.search(self.cli(cmd))
        if match:
            return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"),
            }
        return {"success": 0, "count": count}
