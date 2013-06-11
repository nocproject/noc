# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.TIMOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
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
    name = "Alcatel.TIMOS.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    rx_id = re.compile(r"^\s*Base MAC address\s*:\s*(?P<id>\S+)",
                       re.IGNORECASE | re.MULTILINE)

    def execute(self):
        v = self.cli("show chassis")
        match = self.re_search(self.rx_id, v)
        base = match.group("id")

        return {
            "first_chassis_mac": base,
            "last_chassis_mac": base
        }