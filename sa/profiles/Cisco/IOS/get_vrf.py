# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_vrf
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVRF


class Script(NOCScript):
    name = "Cisco.IOS.get_vrf"
    implements = [IGetVRF]

    rx_line = re.compile(r"^\s+(?P<vrf>.+?)\s+"
                         r"(?P<rd>\S+:\S+)\s+(?P<iface>.+?)\s*$")
    rx_cont = re.compile("^\s{6,}(?P<iface>.+?)\s*$")

    def execute(self, **kwargs):
        vrfs = []
        v = self.cli("show ip vrf")
        for l in v.splitlines():
            match = self.rx_line.match(l)
            if match:
                vrfs += [{
                    "name": match.group("vrf"),
                    "rd": match.group("rd"),
                    "interfaces": [match.group("iface")]
                }]
            elif vrfs:
                match = self.rx_cont.match(l)
                if match:
                    vrfs[-1]["interfaces"] += [match.group("iface")]
        return vrfs
