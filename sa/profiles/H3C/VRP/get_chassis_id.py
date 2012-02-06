# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## H3C.VRP.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "H3C.VRP.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    rx_mac_old = re.compile(r"MAC address[^:]*?:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    @NOCScript.match(version__startswith="3.02")
    def execute_old(self):
        v = self.cli("display stp")
        match = self.re_search(self.rx_mac_old, v)
        return match.group("id")

    rx_mac = re.compile(r"^CIST Bridge[^:]*?:\s*\d+?\.(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    @NOCScript.match()
    def execute_new(self):
        v = self.cli("display stp")
        match = self.re_search(self.rx_mac, v)
        return match.group("id")
