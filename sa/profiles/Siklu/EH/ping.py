# ---------------------------------------------------------------------
# Siklu.EH.ping
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
    name = "Siklu.EH.ping"
    interface = IPing
    # 5 packets transmitted, 5 received, 0% packet loss, time 3999ms
    # rtt min/avg/max/mdev = 0.058/0.063/0.083/0.013 ms
    rx_result = re.compile(
        r"^(?P<count>\d+)\s+packets transmitted,\s+"
        r"(?P<success>\d+)\s+received,.*?"
        r"rtt min/avg/max/mdev\s+=\s+(?P<min>\S+)/(?P<avg>\S+)/(?P<max>\S+)/",
        re.MULTILINE | re.DOTALL,
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = "ping %s" % address
        if count:
            cmd += " -c %d" % int(count)
        else:
            cmd += " -c 5"
        if size:
            cmd += " -l %d" % int(size)
        pr = self.cli(cmd)
        match = self.rx_result.search(pr)
        return {
            "success": match.group("success"),
            "count": match.group("count"),
            "min": match.group("min"),
            "avg": match.group("avg"),
            "max": match.group("max"),
        }
