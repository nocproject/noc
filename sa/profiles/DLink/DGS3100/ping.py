# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPing
import re


class Script(NOCScript):
    name = "DLink.DGS3100.ping"
    implements = [IPing]
    rx_result = re.compile(r"^\s*Packets: Sent =\s*(?P<count>\d+), Received =\s*(?P<success>\d+), Lost =\s*\d+", re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_dgs3100 = re.compile(r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets received, \d+% packet loss\nround-trip \(ms\) min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)", re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_dgs3100_nr = re.compile(r"^\s*(?P<count>\d+) packets transmitted, 0 packets received, 100% packet loss", re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(self, address, count=None):
        cmd = "ping %s" % address
        if count:
            cmd += " times %d" % int(count)
        else:
            cmd += " times 5"
        dgs3100_no_reply = False
        match = self.rx_dgs3100.search(self.cli(cmd))
        if not match:
            # All packet return with "no reply"
            match = self.rx_dgs3100_nr.search(self.cli(cmd))
            dgs3100_no_reply = True
        if not match:
            raise self.NotSupportedError()
        r = {
            "success": match.group("success") if not dgs3100_no_reply else "0",
            "count": match.group("count"),
        }
        if not dgs3100_no_reply:
            r.update({
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"),
            })
        return r
