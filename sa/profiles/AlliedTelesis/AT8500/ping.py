# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8500.ping
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

rx_result=re.compile(r"^Reply from [\d\.]+ time=(?P<resp>\d+)ms$",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="AlliedTelesis.AT8500.ping"
    implements=[IPing]
    def execute(self,address,size=None,count=None,timeout=None):
        cmd="ping %s"%address
        pr=self.cli(cmd)
        r=[]
        n=0
        for l in pr.split("\n"):
            match=rx_result.match(l.strip())
            if match:
                r.append(match.group("resp"))
                n+=int(match.group("resp"))
        avg1=int(n/len(r))
        return {
                "success" : len(r),
                "count" : 4,
                "min" : min(r),
                "avg" : avg1,
                "max": max(r)
               }
