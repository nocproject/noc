# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
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
    rx_result = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, \d+\.\d+% packet loss\nround-trip min/avg/max/stddev = "
        r"(?P<min>\d+\.\d+)/(?P<avg>\d+\.\d+)/(?P<max>\d+\.\d+)/\d+\.\d+ ms",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_result1 = re.compile(
        r"^\s*(?P<count>\d+) packets transmitted, (?P<success>\d+) packets "
        r"received, \d+\.\d+% packet loss\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

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
        s = self.cli(cmd)
        match = self.rx_result.search(s)
        if match:
            return {
                "success": match.group("success"),
                "count": match.group("count"),
                "min": match.group("min"),
                "avg": match.group("avg"),
                "max": match.group("max")
            }
        else:
            match = self.rx_result1.search(s)
            return {
                "success": match.group("success"),
                "count": match.group("count")
            }
