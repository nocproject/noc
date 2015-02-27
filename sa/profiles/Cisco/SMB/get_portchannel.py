# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SMB.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetPortchannel


class Script(noc.sa.script.Script):
    name = "Cisco.SMB.get_portchannel"
    implements = [IGetPortchannel]

    rx_po = re.compile(r"^(?P<pcname>Po\d+)\s*(?P<aports>Active: \S+)?[, ]*(?P<iports>Inactive: \S+)?")

    def execute(self):          # TODO: test with real port-channels
        r = []
        s = self.cli("show interfaces Port-Channel", cached=True)
        for l in s.split("\n"):
            match = self.rx_po.match(l.strip())
            if not match:
                continue
            else:
                pc = match.group("pcname")
                try:
                    aports = match.group("aports")
                    aports = map(self.profile.convert_interface_name,aports.split(","))
                except:
                    aports = []
            r += [{
                "interface": pc,
                "members": aports, # <!> TODO: inactive ports???
                "type": "S",   # <!> TODO: port-channel type detection (LACP)
            }]
        return r
