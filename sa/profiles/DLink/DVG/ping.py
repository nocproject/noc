# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DVG.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IPing


class Script(noc.sa.script.Script):
    name = "DLink.DVG.ping"
    implements = [IPing]

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) (packets received|received), \d+% packet loss$",
        re.MULTILINE)
    rx_stat = re.compile(
        r"^round-trip min/avg/max = (?P<min>.+)/(?P<avg>.+)/(?P<max>.+) ms$",
        re.MULTILINE)

    def execute(self, address, count=None, source_address=None, size=None,
                df=None):
        cmd = "ping %s" % address
        if count:
            cmd += " %d" % int(count)
        else:
            cmd += " 5"
        if size:
            cmd += " %d" % int(size)
        else:
            cmd += " 64"
        ping = self.cli(cmd)
        result = self.rx_result.search(ping)
        if result:
            r = {
                "success": result.group("success"),
                "count": result.group("count"),
                }
        else:
            raise self.NotSupportedError()
        stat = self.rx_stat.search(ping)
        if stat:
            r.update({
                "min": stat.group("min"),
                "avg": stat.group("avg"),
                "max": stat.group("max"),
                })
        return r
