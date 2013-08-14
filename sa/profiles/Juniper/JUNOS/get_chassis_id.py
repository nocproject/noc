# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
from noc.lib.mac import MAC


class Script(NOCScript):
    name = "Juniper.JUNOS.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    rx_range = re.compile(
        "Public base address\s+(?P<mac>\S+)\s+"
        "Public count\s+(?P<count>\d+)",
        re.DOTALL | re.IGNORECASE
    )

    def execute(self):
        v = self.cli("show chassis mac-addresses")
        return [
            {
                "first_chassis_mac": mac,
                "last_chassis_mac": MAC(mac).shift(int(count))
            } for mac, count in self.rx_range.findall(v)
        ]
