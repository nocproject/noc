# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
""" 
""" 
import noc.sa.script
from noc.sa.interfaces import IGetARP
import re

class Script(noc.sa.script.Script):
    name="DLink.DxS.get_arp" 
    implements=[IGetARP]
    rx_line=re.compile(r"^(?P<interface>\S+)\s+(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(?P<mac>\S+)\s+\S+$")
    def execute(self):
        s=self.cli("show arpentry")
        r=[]
        for l in s.split("\n"):
            match=self.rx_line.match(l.strip())
            if not match:
                continue
            r.append({"ip":match.group("ip"),"mac":match.group("mac"),"interface":match.group("interface")})
        return r
