# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.ping
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
    name = "OS.FreeBSD.ping"
    implements = [IPing]
    rx_result = re.compile(r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets received, \d+\.\d+% packet loss\nround-trip min/avg/max/stddev = (?P<min>\d+\.\d+)/(?P<avg>\d+\.\d+)/(?P<max>\d+\.\d+)/\d+\.\d+ ms", re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(self, address, count=None, source_address=None, size=None,
    df=None):
        cmd = "ping -q"
        if count:
            cmd += " -c %d" % int(count)
        else:
            cmd += " -c 5"
        if source_address:
            cmd += " -S %s" % source_address
        if size:
            cmd += " -s %d" % int(size)
        if df:
            cmd += " -D"
        cmd += " %s" % address
        match = self.rx_result.search(self.cli(cmd))
        return {
            "success": match.group("success"),
            "count": match.group("count"),
            "min": match.group("min"),
            "avg": match.group("avg"),
            "max": match.group("max"),
        }
