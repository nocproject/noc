# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1910.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "HP.1910.ping"
    interface = IPing

    rx_result = re.compile(
        r"\s+(?P<count>\d+) packet\(s\) transmitted.\s+(?P<success>\d+) packet\(s\) received.\s+\S+% packet loss.\s+round-trip min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+) ms",
        re.DOTALL | re.MULTILINE)

    def execute(self, address, count=None, source_address=None,
        size=None, df=None):
        cmd = "ping -q"
        if df:
            cmd+=" -f"
        if count:
            cmd += " -c %d" % int(count)
        if size:
            cmd += " -s %d" % int(size)
        if source_address:
            cmd +=" -a %s" % source_address
        cmd += " %s" % address
        ping = self.cli(cmd)
        result = self.rx_result.search(ping)
        r = {
            "success": result.group("success"),
            "count": result.group("count"),
            "min": result.group("min"),
            "avg": result.group("avg"),
            "max": result.group("max")
            }
        return r
