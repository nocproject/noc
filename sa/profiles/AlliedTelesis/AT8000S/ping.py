# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.ping
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IPing
import re

rx_result=re.compile(r"^(?P<count>\d+) packets transmitted, (?P<success>\d+) packets received, \d+% packet loss\nround-trip \(ms\) min/avg/max = (?P<min>\d+)/(?P<avg>\d+)/(?P<max>\d+)?",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="AlliedTelesis.AT8000S.ping"
    implements=[IPing]
    def execute(self,address,size=None,count=None,timeout=None):
        cmd="ping %s"%address
        if size:
            cmd+=" size %d"%int(size)
        if count:
            cmd+=" count %d"%int(count)
        if timeout:
            cmd+=" timeout %d"%int(timeout)
        pr=self.cli(cmd)
        pr=self.strip_first_lines(pr,1)
        match=rx_result.search(pr)
        return {
                "success": match.group("success"),
                "count"  : match.group("count"),
                "min"    : match.group("min"),
                "avg"    : match.group("avg"),
                "max"    : match.group("max"),
            }
