# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Opticin.OS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable, MACAddressParameter

class Script(BaseScript):
    name = "Opticin.OS.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_macs = re.compile(r"^(?P<mac>\S+)\s+(?P<type>\S+)$", re.MULTILINE | re.IGNORECASE | re.DOTALL)

    types = {
        "learned": "D",
        "permanent": "S",
        "dynamic": "D",
        "static": "S",
        "learn": "D",
        "cpu": "S"
    }

    def execute(self, interface=None, vlan=None, mac=None):
        
        cmd = "sh port mac-learning"
        if interface is not None:
            cmd += " %s" % int(interface.replace("Port", ""))
            macs = self.cli(cmd)
            r = []
            for l in macs.splitlines():
                match = self.rx_macs.match(l)
                if match:
                    mac = MACAddressParameter().clean(match.group("mac"))
                    type = match.group("type")
                    vlan = "1"
                    intf = [interface]
                    r += [{
                        "vlan_id": vlan,
                        "mac": mac,
                        "interfaces": intf,
                        "type": self.types[type.lower()]
                    }]
            return r
        else:
            r = []
            for i in self.scripts.get_interface_status():
                if i["status"] == False:
                   continue
                else:
                    cmd = "sh port mac-learning"
                    port = i["interface"]
                    cmd += " %s" % int(port.replace("Port", ""))
                    macs = self.cli(cmd)
                    for l in macs.splitlines():
                        match = self.rx_macs.match(l)
                        if match:
                            mac = MACAddressParameter().clean(match.group("mac"))
                            type = match.group("type")
                            vlan = "1"
                            intf = [port]
                            r += [{
                                "vlan_id": vlan,
                                "mac": mac,
                                "interfaces": intf,
                                "type": self.types[type.lower()]
                            }]
            return r
