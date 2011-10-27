# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IPing

rx_result = re.compile(r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) (packets received|received), \d+% packet loss",re.MULTILINE)
rx_stat = re.compile(r"^round-trip (ms) min/avg/max = (?P<min>\d+\.\d+)/(?P<avg>\d+\.\d+)/(?P<max>\d+\.\d+)",re.MULTILINE)

class Script(noc.sa.script.Script):
    name = "Eltex.MES.ping"
    implements = [IPing]

    def execute(self,address,count=None,source_address=None,size=None,df=None):
        cmd="ping ip %s"%address
        if count:
            cmd += " count %d"%int(count)
        if size:
            cmd += " size %d"%int(size)
        # Don't implemented, may be in future firmware revisions ?
        #if source_address:
        #    cmd+=" source %s"%source_address
        #if df:
        #    cmd+=" df-bit"
        min = 0
        avg = 0
        max = 0
        ping = self.cli(cmd)
        result = rx_result.search(ping)
        stat = rx_stat.search(ping)
        if stat:
            min = stat.group("min")
            avg = stat.group("avg")
            max = stat.group("max")
        return {
                "success" : result.group("success"),
                "count"   : result.group("count"),
                "min"     : min,
                "avg"     : avg,
                "max"     : max,
                }
