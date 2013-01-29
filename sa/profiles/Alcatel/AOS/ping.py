# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IPing
import re


class Script(noc.sa.script.Script):
    name = "Alcatel.AOS.ping"
    implements = [IPing]
    rx_result = re.compile(r"^(?P<success>\d+)\s+packets transmitted,\s+(?P<count>\d+)\s+packets received,\s+\d+%\s+packet loss?"
                           r"\nround-trip \(ms\)\s+min/avg/max\s+=\s+(?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)?",
                           re.MULTILINE | re.DOTALL)

    def execute(self, address, count=None, source_address=None, size=None, df=None):
        cmd = "ping %s count 5" % address
        if count:
            cmd += " count %d" % int(count)
        if source_address:
            cmd += " source %s" % source_address
        if size:
            cmd += " size %d" % int(size)
        if df:
            cmd += " df-bit"
        pr = self.cli(cmd)
        match = self.rx_result.search(pr)
        return {"success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max"), }