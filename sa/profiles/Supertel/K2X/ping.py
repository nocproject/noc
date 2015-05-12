# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IPing


class Script(NOCScript):
    name = "Supertel.K2X.ping"
    implements = [IPing]

    rx_result = re.compile(
        r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) "
        r"(packets received|received), \d+% packet loss$",
        re.MULTILINE)
    rx_stat = re.compile(
        r"^round-trip \(ms\) min/avg/max = "
        r"(?P<min>.+)/(?P<avg>.+)/(?P<max>.+)$",
        re.MULTILINE)

    def execute(self, address, count=None, source_address=None,
                size=None, df=None):
        if ':' in address:
            cmd = "ping ipv6 %s" % address
        else:
            cmd = "ping %s" % address
        if size:
            cmd += " size %d" % int(size)
        if count:
            cmd += " count %d" % int(count)
        """
        # Don't implemented, may be in future firmware revisions ?
        if source_address:
            cmd+=" source %s" % source_address
        if df:
            cmd+=" df-bit"
        """
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
