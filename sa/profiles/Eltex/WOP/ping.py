# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.WOP.ping
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
    name = "Eltex.WOP.ping"
    interface = IPing

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) "
        r"(packets received|received),(?:\s|\s\S+ (errors|duplicates), )\d+% packet loss$",
        re.MULTILINE,
    )
    rx_stat = re.compile(
        r"^round-trip min/avg/max = (?P<min>.+)/(?P<avg>.+)/(?P<max>.+)\s.", re.MULTILINE
    )
    rx_count = re.compile(r"^\d+ bytes from \d\S+\d+: seq=(\d+) ttl=\d+ time=\S+ ms", re.MULTILINE)

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        if count is None:
            count = 5
        cmd = "ping %s -c %d" % (address, int(count))
        if size:
            cmd += " -s %d" % int(size)
        if source_address:
            cmd += " -I %s" % source_address
        result = None
        try:
            ping = self.cli(cmd, ignore_errors=True)
            result = self.rx_result.search(ping)
        except self.CLISyntaxError:
            pass

        """
        Workaround for this incident

        PING 10.1.1.1 (10.1.1.1): 56 data bytes
        64 bytes from 10.1.1.1: seq=0 ttl=61 time=15.436 ms
        64 bytes from 10.1.1.1: seq=1 ttl=61 time=15.265 ms
        64 bytes from 10.1.1.1: seq=2 ttl=61 time=15.365 ms
        ping: sendto: Network is unreachable
        Invalid command.

        """
        if not result and "Network is unreachable" in ping:
            result = self.rx_count.findall(ping)
            return {"success": len(result), "count": count}

        r = {"success": result.group("success"), "count": result.group("count")}
        stat = self.rx_stat.search(ping)
        if stat:
            r.update({"min": stat.group("min"), "avg": stat.group("avg"), "max": stat.group("max")})
        return r
