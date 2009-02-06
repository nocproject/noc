# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetDot11Associations
import re

rx_assoc_line=re.compile(r"^(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}) (?P<ip>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*$")

class Script(noc.sa.script.Script):
    name="Cisco.IOS.get_dot11_associations"
    implements=[IGetDot11Associations]
    def execute(self):
        self.cli("terminal length 0")
        assoc=self.cli("show dot11 associations")
        r=[]
        for l in assoc.split("\n"):
            match=rx_assoc_line.match(l.strip())
            if match:
                r.append({"mac":match.group("mac"),"ip":match.group("ip")})
        return r
