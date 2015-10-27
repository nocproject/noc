# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linksys.SPS2xx.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable


class Script(NOCScript):
    name = "Linksys.SPS2xx.get_mac_address_table"
    implements = [IGetMACAddressTable]
    cached = True

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interfaces>\S+)\s+(?P<type>\S+)",
        re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        # Try SNMP first
        if self.has_snmp():
            try:
                vlan_oid = []
                if mac is not None:
                    mac = mac.lower()
                for v in self.snmp.get_tables(["1.3.6.1.2.1.17.7.1.2.2.1.2"],
                        bulk=True):
                        vlan_oid.append(v[0])
                # mac iface type
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.17.4.3.1.1", "1.3.6.1.2.1.17.4.3.1.2",
                    "1.3.6.1.2.1.17.4.3.1.3"], bulk=True):
                    if v[1]:
                        chassis = ":".join(["%02x" % ord(c) for c in v[1]])
                        if mac is not None:
                            if chassis == mac:
                                pass
                            else:
                                continue
                    else:
                        continue
                    if int(v[3]) > 3 or int(v[3]) < 1:
                        continue
                    iface = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1." + v[2],
                            cached=True)  # IF-MIB
                    if interface is not None:
                        if iface == interface:
                            pass
                        else:
                            continue
                    for i in vlan_oid:
                        if v[0] in i:
                            vlan_id = int(i.split('.')[0])
                            break
                    if vlan is not None:
                        if vlan_id == vlan:
                            pass
                        else:
                            continue

                    r.append({
                        "interfaces": [iface],
                        "mac": chassis,
                        "type": {"3": "D", "2": "S", "1": "S"}[v[3]],
                        "vlan_id": vlan_id,
                        })
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        cmd = "show mac address-table"
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for match in self.rx_line.finditer(self.cli(cmd, cached=True)):
                interfaces = match.group("interfaces")
                if interfaces == '0':
                    continue
                if interface is not None:
                    if interfaces == interface:
                        r += [{"vlan_id": match.group("vlan_id"),
                            "mac": match.group("mac"),
                            "interfaces": [interfaces],
                            "type": {
                                "dynamic": "D",
                                "static": "S",
                                "permanent": "S",
                                "self": "S"}[match.group("type").lower()],
                            }]
                else:
                    r += [{"vlan_id": match.group("vlan_id"),
                        "mac": match.group("mac"),
                        "interfaces": [interfaces],
                        "type": {
                            "dynamic": "D",
                            "static": "S",
                            "permanent": "S",
                            "self": "S"}[match.group("type").lower()],
                        }]
        return r
