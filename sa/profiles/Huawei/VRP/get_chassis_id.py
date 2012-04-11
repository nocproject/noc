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


class Script(noc.sa.script.Script):
    name = "Huawei.VRP.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    rx_mac = re.compile(r"MAC address[^:]*?:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)
    rx_mac1 = re.compile(r"CIST Bridge\s+:\d+\.(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    def execute(self):
        v = self.cli("display stp")
        match = self.rx_mac.search(v)
        if match:
            return match.group("id")
        else:
            match = self.rx_mac1.search(v)
            if match:
                return match.group("id")

        raise self.NotSupportedError()
