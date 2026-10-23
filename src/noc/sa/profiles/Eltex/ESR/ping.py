# ---------------------------------------------------------------------
# Eltex.ESR.ping
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
    name = "Eltex.ESR.ping"
    interface = IPing

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) (packets received|received), \d+% packet loss",
        re.MULTILINE,
    )
    rx_stat = re.compile(
        r"^rtt min/avg/max/mdev = (?P<min>.+)/(?P<avg>.+)/(?P<max>.+)/(\S+) ms", re.MULTILINE
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = f"ping ip {address}"
        if count:
            cmd += f" packets {int(count)}"
        else:
            cmd += " packets 3"
        if size:
            cmd += f" size {int(size)}"
        if source_address:
            cmd += f" source {source_address}"
        # if df:
        #    cmd+=" df-bit"
        ping = self.cli(cmd)
        result = self.rx_result.search(ping)
        r = {"success": result.group("success"), "count": result.group("count")}
        stat = self.rx_stat.search(ping)
        if stat:
            r.update({"min": stat.group("min"), "avg": stat.group("avg"), "max": stat.group("max")})
        return r
