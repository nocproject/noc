# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    rx_chassis_id = re.compile(r"Ethernet Address\s+:\s*(?P<id>\S+)",
                            re.IGNORECASE | re.MULTILINE)

    def execute(self):
        v = self.cli("show system-information")
        match = self.rx_chassis_id.search(v)
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
