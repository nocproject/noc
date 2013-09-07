# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOSXR.get_chassis_id
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
    name = "Cisco.IOSXR.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    rx_range = re.compile(
        r"Base MAC Address\s*:\s*(?P<mac>\S+)\s+"
        r"MAC Address block size\s*:\s*(?P<count>\d+)",
        re.DOTALL | re.IGNORECASE
    )

    def execute(self):
        v = self.cli("admin show diag chassis eeprom-info")
        macs = []
        for f, t in [(mac, MAC(mac).shift(int(count) - 1))
                for mac, count in self.rx_range.findall(v)]:
            if macs and MAC(f).shift(-1) == macs[-1][1]:
                macs[-1][1] = t
            else:
                macs += [[f, t]]
        return [
            {
                "first_chassis_mac": f,
                "last_chassis_mac": t
            } for f, t in macs
        ]
