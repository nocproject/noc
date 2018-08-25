# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DCN.DCWL.ping
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "DCN.DCWL.ping"
    interface = IPing

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) (packets received|received),(?:\s|\s\S+ errors, )\d+% packet loss$",
        re.MULTILINE)
    rx_stat = re.compile(
        r"^round-trip min/avg/max = (?P<min>.+)/(?P<avg>.+)/(?P<max>.+)\s.",
        re.MULTILINE)

    def execute(self, address, count=None, source_address=None,
                size=None, df=None):
        cmd = "ping %s -c 5" % address
        if count:
            cmd += " count %d" % int(count)
        if size:
            cmd += " size %d" % int(size)
        # Don't implemented, may be in future firmware revisions ?
        # if source_address:
        #    cmd+=" source %s" % source_address
        # if df:
        #    cmd+=" df-bit"
        ping = self.cli(cmd)
        result = self.rx_result.search(ping)
        r = {
            "success": result.group("success"),
            "count": result.group("count"),
        }
        stat = self.rx_stat.search(ping)
        if stat:
            r.update({
                "min": stat.group("min"),
                "avg": stat.group("avg"),
                "max": stat.group("max"),
            })
        return r
