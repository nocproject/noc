# -*- coding: utf-8 -*-
##----------------------------------------------------------------
## Huawei.VRP.get_oam_status
##----------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetOAMStatus
from noc.sa.interfaces.base import MACAddressParameter


class Script(BaseScript):
    name = "Huawei.VRP.get_oam_status"
    interface = IGetOAMStatus

    rx_line = re.compile(r"""
    \s+Interface:\s+(?P<interface>.+?)\n
    .+?
    Remote\sMAC:\s+(?P<mac>.+?)\n
    """, re.VERBOSE | re.DOTALL | re.MULTILINE)
    oam_splitter = re.compile(r"\s+-{52}(?P<oam>.+?)Remote\sEFM",
         re.DOTALL | re.MULTILINE)

    def execute(self, **kwargs):
        r = []
        try:
            v = self.cli("display efm all")
        except self.CLISyntaxError:
            raise self.NotSupportedError
        oams = re.findall(self.oam_splitter, v)
        if not oams:
            raise self.NotSupportedError
        for l in oams:
            match = self.rx_line.match(l)
            if match:
                iface = match.group("interface").strip()
                mac = match.group("mac")
                try:
                    mac=MACAddressParameter().clean(mac)
                except:
                   continue
                r += [{
                    "interface": iface,
                    "remote_mac": mac,
                    "caps": ["L"]
                }]
        return r
