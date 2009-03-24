# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
# Force10.FTOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
import re

rx_header_line=re.compile(r"^([\-]+)(\s+)([\-]+)\s.*$")

class Script(noc.sa.script.Script):
    name="Force10.FTOS.get_vlans"
    implements=[IGetVlans]
    def execute(self):
        self.cli("terminal length 0")
        vlans=self.cli("show vlan brief")
        r=[]
        fl=0
        sl=0
        ssl=0
        for l in vlans.split("\n"):
            l=l.strip()
            if not l:
                continue
            if not fl:
                if l.startswith("-"):
                    match=rx_header_line.match(l)
                    if match:
                        fl=len(match.group(1))
                        ssl=len(match.group(2))
                        sl=len(match.group(3))
                        continue
            else:
                r.append({"vlan_id": int(l[:fl].strip()),
                          "name"   : l[fl+ssl:fl+ssl+sl].strip()})
        return r
