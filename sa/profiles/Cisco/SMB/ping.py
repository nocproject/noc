# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SMB.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing


class Script(BaseScript):
    name = "Cisco.SMB.ping"
    interface = IPing
    rx_result = re.compile(r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) packets received.*round-trip \(ms\) min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)", re.MULTILINE | re.DOTALL)

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = "ping ip %s" % address
        if count:
            cmd += " count %d" % int(count)
        if source_address:
            cmd += " source %s" % source_address
        if size:
            cmd += " size %d" % int(size)
        if df:
            # no such option in CLI:
            raise self.NotSupportedError()
            cmd += " df-bit"
        pr = self.cli(cmd)
        match = self.rx_result.search(pr)
        return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"),
            }
