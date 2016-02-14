# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.ping
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
    name = "EdgeCore.ES.ping"
    interface = IPing
    rx_rtt = re.compile(
        r"Minimum = (?P<min>\d+) ms, Maximum = (?P<max>\d+) ms, Average = (?P<avg>\d+) ms"
    )
    rx_count = re.compile(
        r"(?P<count>\d+) packets transmitted, (?P<success>\d+) packets received"
    )

    def execute(self, address, count=None, source_address=None,
                size=None, df=None, vrf=None):
        cmd = "ping ip %s" % address
        if count:
            cmd += " count %d" % int(count)
        if size:
            cmd += " size %d" % int(size)
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
