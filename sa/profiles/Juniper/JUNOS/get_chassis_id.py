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
        "(?P<type>Public|Private) base address\s+(?P<mac>\S+)\s+"
        "(?P=type) count\s+(?P<count>\d+)",
        re.DOTALL | re.IGNORECASE
    )

    def execute(self):
        v = self.cli("show chassis mac-addresses")
        macs = []
        for f, t in [(mac, MAC(mac).shift(int(count) - 1))
                for _, mac, count in self.rx_range.findall(v)]:
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
