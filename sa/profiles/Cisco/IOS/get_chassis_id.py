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

rx_ver=re.compile(r"^Base ethernet MAC Address\s*:\s*(?P<id>\S+)",re.IGNORECASE|re.MULTILINE)
rx_cat6000=re.compile(r"chassis MAC addresses:.+from\s+(?P<id>\S+)\s+to",re.IGNORECASE|re.MULTILINE)

class Script(noc.sa.script.Script):
    name="Cisco.IOS.get_chassis_id"
    implements=[IGetChassisID]
    def execute(self):
        v=self.scripts.get_version()["version"]
        if "SE" in v:
            # 2960/3560/3750/3120
            v=self.cli("show version")
            match=rx_ver.search(v)
            return match.group("id")
        elif "SX" in v or "SR" in v:
            # 6500/7600 series
            v=self.cli("show catalyst6000 chassis-mac-addresses")
            match=rx_cat6000.search(v)
            return match.group("id")
        raise Exception("Unsupported platform")
        