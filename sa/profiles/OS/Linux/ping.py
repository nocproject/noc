# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.Linux.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPing


class Script(NOCScript):
    name = "OS.Linux.ping"
    implements = [IPing]

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) (packets received|received),+( |\+\d+ errors, )+\d+% packet loss",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_stat = re.compile(
        r"^\S+ min/avg/max(/mdev | )= (?P<min>\d+\.\d+)/(?P<avg>\d+\.\d+)/(?P<max>\d+\.\d+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(self, address, count=None, source_address=None,
                size=None, df=None):
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
