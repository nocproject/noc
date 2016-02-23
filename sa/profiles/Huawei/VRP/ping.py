# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Huawei.VRP.ping"
    interface = IPing
    rx_rtt = re.compile(
        r"round-trip min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+) ms"
    )
    rx_count = re.compile(
        r"(?P<count>\d+) packet\(s\) transmitted.+(?P<success>\d+) packet\(s\) received",
        re.MULTILINE | re.DOTALL
    )

    def execute(self, address, count=None, source_address=None,
                size=None, df=None, vrf=None):
        cmd = "ping -q"
        if count:
            cmd += " -c %d" % int(count)
        if size:
            cmd += " -s %d" % int(size)
        if source_address:
            cmd += " -a %s" % source_address
        cmd += " %s" % address
        pr = self.cli(cmd)
        m1 = self.re_search(self.rx_count, pr)
        m2 = self.re_search(self.rx_rtt, pr)
        return {
            "success": m1.group("success"),
            "count": m1.group("count"),
            "min": m2.group("min"),
            "avg": m2.group("avg"),
            "max": m2.group("max"),
        }
