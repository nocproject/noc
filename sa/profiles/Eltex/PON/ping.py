# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.PON.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Eltex.PON.ping"
    interface = IPing

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, \d+% packet loss$", re.MULTILINE)
    rx_stat = re.compile(
        r"^round-trip min/avg/max = (?P<min>.+)/(?P<avg>.+)/(?P<max>.+) ms$",
        re.MULTILINE)

    def execute(self, address, count=None, source_address=None,
        size=None, df=None):
        cmd = "ping %s" % address
        """
        # Don't implemented, may be in future firmware revisions ?
        if count:
            cmd += " count %d" % int(count)
        if size:
            cmd += " size %d" % int(size)
        if source_address:
            cmd+=" source %s" % source_address
        if df:
            cmd+=" df-bit"
        """
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
