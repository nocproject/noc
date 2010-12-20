# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Unix.FreeBSD.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetARP
##
## OS.FreeBSD.get_arp
##
class Script(noc.sa.script.Script):
    name="OS.FreeBSD.get_arp"
    implements=[IGetARP]
    
    rx_line=re.compile(r"^\S+\s+\((?P<ip>\S+)\)\s+\S+\s+(?P<mac>\S+)\s+\S+\s+(?P<interface>\S+)",re.MULTILINE|re.DOTALL)
    def execute(self):
        s=self.cli("/usr/sbin/arp -an")
        r=[]
        for match in self.rx_line.finditer(s):
            r+=[{
                "ip"        :match.group("ip"),
                "mac"       :match.group("mac"),
                "interface" :match.group("interface")
                }]
        return r
    
