# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS_EE.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable


class Script(NOCScript):
    name = "Zyxel.ZyNOS_EE.get_mac_address_table"
    implements = [IGetMACAddressTable]

    rx_line = re.compile(
        r"^\S+\s+(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+\d+\s+\d+\s+(?P<interfaces>\d+)\s+\d+\s+(?P<type>\d+)")

    def execute(self, interface=None, vlan=None, mac=None):
        if interface is not None:
            cmd = "sys sw mac list %s" % interface
        elif mac and vlan is not None:
            mac = mac.lower().replace(':', '')
            cmd = "sys sw mac search %s %s" % (mac, vlan)
        else:
            cmd = "sys sw mac list all"

        macs = self.cli(cmd)
        r = []
        if mac is not None:
            mac = mac.replace(':', '').lower()
            for l in macs.split("\n"):
                match = self.rx_line.match(l.strip())
                if match:
                    mac_address = match.group("mac")
                    vlan_id = match.group("vlan_id")
                    if mac_address == mac:
                        r.append({
                            "vlan_id": vlan_id,
                            "mac": mac_address,
                            "interfaces": [match.group("interfaces")],
                            "type": {"01": "D", "00": "S"}[match.group("type")]
                            })
        elif vlan is not None:
            for l in macs.split("\n"):
                match = self.rx_line.match(l.strip())
                if match:
                    mac_address = match.group("mac")
                    vlan_id = match.group("vlan_id")
                    vlan_id = str(int(vlan_id))
                    if vlan_id == str(vlan):
                        r.append({
                            "vlan_id": vlan_id,
                            "mac": mac_address,
                            "interfaces": [match.group("interfaces")],
                            "type": {"01": "D", "00": "S"}[match.group("type")]
                            })
        else:
            for l in macs.split("\n"):
                match = self.rx_line.match(l.strip())
                if match:
                    mac_address = match.group("mac")
                    vlan_id = match.group("vlan_id")
                    r.append({
                        "vlan_id": vlan_id,
                        "mac": mac_address,
                        "interfaces": [match.group("interfaces")],
                        "type": {"01": "D", "00": "S"}[match.group("type")],
                        })

        return r
