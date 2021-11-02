# ---------------------------------------------------------------------
# Rotek.RTBSv1.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Rotek.RTBSv1.ping"
    interface = IPing

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) (packets received|received),(?:\s|\s\S+ errors, )\d+% packet loss.",
        re.MULTILINE,
    )
    rx_stat = re.compile(
        r"^rtt min/avg/max/mdev = (?P<min>.+)/(?P<avg>.+)/(?P<max>.+)/(?P<mdev>.+)\s.", re.MULTILINE
    )

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        try:
            # Linux mode
            cmd = "ping "
            if count:
                cmd += "-c %d " % count
            if size:
                cmd += "-s %d " % size
            cmd += address
            ping = self.cli(cmd)
        except self.CLISyntaxError:
            cmd = "ping %s" % address
            ping = self.cli(cmd)
        # Not works
        # if count:
        #     cmd += " count %d" % int(count)
        # if size:
        #     cmd += " size %d" % int(size)
        # Don't implemented, may be in future firmware revisions ?
        # if source_address:
        #    cmd+=" source %s" % source_address
        # if df:
        #    cmd+=" df-bit"
        if "Network is unreachable" in ping:
            return {"success": 0, "count": count if count else 5}
        result = self.rx_result.search(ping)
        r = {"success": result.group("success"), "count": result.group("count")}
        stat = self.rx_stat.search(ping)
        if stat:
            r.update(
                {
                    "min": stat.group("min"),
                    "avg": stat.group("avg"),
                    "max": stat.group("max"),
                    "mdev": stat.group("mdev"),
                }
            )
        return r
