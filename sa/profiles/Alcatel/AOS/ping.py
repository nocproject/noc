# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iping import IPing
import re


class Script(BaseScript):
    name = "Alcatel.AOS.ping"
    interface = IPing
    rx_result = re.compile(
        r"^(?P<success>\d+)\s+packets transmitted,\s+(?P<count>\d+)\s+"
        r"packets received,\s+\d+%\s+packet loss?\nround-trip \(ms\)\s+"
        r"min/avg/max\s+=\s+(?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)?",
        re.MULTILINE | re.DOTALL)

    def execute(self, address, count=None, source_address=None, size=None, \
        df=None):

        cmd = "ping %s" % address
        if count:
            cmd += " count %d" % int(count)
        else:
            cmd += " count 5"
        if source_address:
            cmd += " source %s" % source_address
        if size:
            cmd += " size %d" % int(size)
        if df:
            cmd += " df-bit"
        pr = self.cli(cmd)
        match = self.rx_result.search(pr)
        return {
            "success": match.group("success"),
            "count": match.group("count"),
            "min": match.group("min"),
            "avg": match.group("avg"),
            "max": match.group("max")
        }
