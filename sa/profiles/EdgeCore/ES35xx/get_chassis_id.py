# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetChassisID
import re

rx_mac=re.compile(r"MAC Address[^:]*?:\s*(?P<id>\S+)",re.IGNORECASE|re.MULTILINE)

class Script(noc.sa.script.Script):
    name="EdgeCore.ES35xx.get_chassis_id"
    implements=[IGetChassisID]
    def execute(self):
        v=self.cli("show system")
        match=rx_mac.search(v)
        return match.group("id")
