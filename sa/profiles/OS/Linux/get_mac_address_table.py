# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.Linux.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable


class Script(noc.sa.script.Script):
    name = "OS.Linux.get_mac_address_table"
    implements = [IGetMACAddressTable]

    rx_vlan = re.compile(
        r"^(?P<interface>\S+)\s+\|+\s+(?P<vlan>\d+)\s+\|+\s+\S+$",
        re.MULTILINE)
    rx_bridge = re.compile(
        r"^(?P<bridge>\S+)+(\s|\t)+\S+(\s|\t)+(no|yes)+(\s|\t)+(?P<interface>\S+)",
        re.MULTILINE)
    rx_bridge_int = re.compile(
        r"^\s+(?P<interface>\S+)", re.MULTILINE)
    rx_showmacs = re.compile(
        r"^\s*(?P<port>\d+)\s+(?P<mac>\S+)\s+(no|yes)\s+(?P<type>\S+)$",
        re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        vlans = {}
        for vl in self.rx_vlan.finditer(self.cli("cat /proc/net/vlan/config")):
            vlan_id = vl.group("vlan")
            if vlan_id not in vlans:
                vlans.update({vlan_id: []})
            vlans[vlan_id].append(vl.group("interface"))

        bridges = {}
        br = self.cli("brctl show").split("\n")
        for i in range(len(br)):
            match = self.rx_bridge.search(br[i])
            if match:
                bridge = match.group("bridge")
                if bridge not in bridges:
                    bridges.update({bridge: []})
                    bridges[bridge].append(match.group("interface"))
                i = i + 1
                match = self.rx_bridge_int.search(br[i])
                while match:
                    bridges[bridge].append(match.group("interface"))
                    i = i + 1
                    match = self.rx_bridge_int.search(br[i])

### This will work only when name of bridge looks like: "'br'+vlan_id"
### We need found more universal way for bind VLAN to bridge, but how???
### Configuration file for vlans is in difirent place in eche
### Linux distribution. Also I don't find any commands or records in /proc...
        r = []
        if mac is not None:
            mac = mac.lower()
        if vlan is not None:
            bridge = 'br' + str(vlan)
            cmd = self.cli("brctl showmacs %s" % bridge)
            for match in self.rx_showmacs.finditer(cmd):
                if match.group("type") == "0.00":
                    typ = "S"
                else:
                    typ = "D"
                interfaces = bridges[bridge][int(match.group("port")) - 1]
                if '.' in interfaces:
                    interfaces = interfaces.split('.')
                    interfaces = interfaces[0]
                if interface is not None:
                    if interface == interfaces:
                        pass
                    else:
                        continue
                chassis = match.group("mac")
                if mac is not None:
                    if chassis == mac:
                        pass
                    else:
                        continue
                r.append({
                    "vlan_id": vlan,
                    "mac": chassis,
                    "interfaces": [interfaces],
                    "type": typ,
                    })
            return r

        for vlan_id in vlans:
            bridge = 'br' + vlan_id
            cmd = self.cli("brctl showmacs %s" % bridge)
            for match in self.rx_showmacs.finditer(cmd):
                if match.group("type") == "0.00":
                    typ = "S"
                else:
                    typ = "D"
                interfaces = bridges[bridge][int(match.group("port")) - 1]
                if '.' in interfaces:
                    interfaces = interfaces.split('.')
                    interfaces = interfaces[0]
                if interface is not None:
                    if interface == interfaces:
                        pass
                    else:
                        continue
                chassis = match.group("mac")
                if mac is not None:
                    if chassis == mac:
                        pass
                    else:
                        continue
                r.append({
                    "vlan_id": vlan_id,
                    "mac": match.group("mac"),
                    "interfaces": [interfaces],
                    "type": typ,
                    })
        return r
