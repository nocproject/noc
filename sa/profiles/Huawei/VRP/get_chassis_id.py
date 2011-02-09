# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetChassisID
##
## Huawei.VRP.get_chassis_id
##
class Script(noc.sa.script.Script):
    name="Huawei.VRP.get_chassis_id"
    cache=True
    implements=[IGetChassisID]
    
    rx_mac=re.compile(r"MAC address[^:]*?:\s*(?P<id>\S+)",re.IGNORECASE|re.MULTILINE)
    def execute(self):
        v=self.cli("display stp")
        match=self.re_search(self.rx_mac, v)
        return match.group("id")
    
