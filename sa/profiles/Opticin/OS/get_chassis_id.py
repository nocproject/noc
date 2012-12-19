# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Opticin.OS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID, MACAddressParameter

class Script(NOCScript):
    name = "Opticin.OS.get_chassis_id"
    cache = True
    implements = [IGetChassisID]
    rx_mac = re.compile(r"System MAC[^:]*?:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    ##
    ## Other
    ##
    @NOCScript.match()
    def execute_other(self):
        v = self.cli("show system")
        match = self.re_search(self.rx_mac, v)
        mac = MACAddressParameter().clean(match.group("id"))
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
