# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.ping
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
    name = "Qtech.QSW2800.ping"
    interface = IPing

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) (packets received|received), \d+% packet loss$",
        re.MULTILINE)
    rx_stat = re.compile(
        r"^round-trip \(ms\)\s+min/avg/max = (?P<min>.+)/(?P<avg>.+)/(?P<max>.+)$",
        re.MULTILINE)

    def execute(self, address, count=None, source_address=None,
        size=None, df=None):
        cmd = "ping"
        if count:
            cmd += " -c %d" % int(count)
        if size:
            cmd += " -s %d" % int(size)


        cmd += " %s" % address
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
