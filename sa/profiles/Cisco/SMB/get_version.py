# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SMB.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Cisco.SMB.get_version"
    cache = True
    implements = [IGetVersion]

    rx_ver = re.compile(
        r"^SW version\s+(?P<version>[^\s,]+).+"
        r"Boot version\s+(?P<bootver>[^\s,]+).+"
        r"HW version\s+(?P<hwver>[^\s]+)", re.MULTILINE | re.DOTALL)
    rx_platform = re.compile(
        r"System Description:\s+(?P<platform>.+)\n", re.IGNORECASE)
    rx_inventory = re.compile(
        r"^PID:\s*(?P<pid>\S+)\s+VID:\s*\S+\s+SN:\s*(?P<sn>\S+)\s*$", re.MULTILINE)

    def execute(self):
        v = self.cli("show version", cached=True)
        vmatch = self.re_search(self.rx_ver, v)
        s = self.cli("show system", cached=True)
        pmatch = self.re_search(self.rx_platform, s)
        try:
            i = self.cli("show inventory", cached=True)
            imatch = self.re_search(self.rx_inventory, i)
            pid = imatch.group("pid")
            sn = imatch.group("sn")
        except:
            pid = None
            sn = None
        return {
            "vendor": "Cisco",
            "platform": pmatch.group("platform"),
            "version": vmatch.group("version"),
            "attributes": {
                "bootrom": vmatch.group("bootver"),
                "hwversion": vmatch.group("hwver"),
                "pid": pid,
                "sn": sn,
            }
        }
