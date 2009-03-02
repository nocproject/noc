# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IPing
import re

rx_result=re.compile(r"^Success rate is \d+ percent \((?P<success>\d+)/(?P<count>\d+)\)(, round-trip min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+) ms)?",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Cisco.IOS.ping"
    implements=[IPing]
    def execute(self,address,count=None,source_address=None,size=None,df=None):
        cmd="ping ip %s"%address
        if count:
            cmd+=" count %d"%int(count)
        if source_address:
            cmd+=" source %s"%source_address
        if size:
            cmd+=" size %d"%int(size)
        if df:
            cmd+=" df-bit"
        pr=self.cli(cmd)
        match=rx_result.search(pr)
        return {
                "success": match.group("success"),
                "count"  : match.group("count"),
                "min"    : match.group("min"),
                "avg"    : match.group("avg"),
                "max"    : match.group("max"),
            }
