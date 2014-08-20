# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Smart.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable


class Script(NOCScript):
    name = "DLink.DxS_Smart.get_mac_address_table"
    implements = [IGetMACAddressTable]
    cached = True

    rx_line = re.compile(
        r"(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>Learnt|Static)\s+"
        r"(?P<interfaces>\S+)", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                vlan_oid = []
                if mac is not None:
                    mac = mac.lower()
                for v in self.snmp.get_tables(
                        ["1.3.6.1.2.1.17.7.1.2.2.1.2"],
                        bulk=True):
                    vlan_oid.append(v[0])

                # mac iface type
                for v in self.snmp.get_tables([
                        "1.3.6.1.2.1.17.7.1.2.2.1.2",
                        "1.3.6.1.2.1.17.7.1.2.2.1.3", ], bulk=True):
                    if v[1]:
                        macar = v[0].split('.')[1:]
                        chassis = ":".join(["%02x" % int(c) for c in macar])
                        if mac is not None:
                            if chassis == mac:
                                pass
                            else:
                                continue
                    else:
                        continue
                    if int(v[2]) > 3 or int(v[2]) < 1:
                        continue
                    iface = self.snmp.get(
                        "1.3.6.1.2.1.31.1.1.1.1." + v[1],
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
                        "type": {"3": "D", "2": "S", "1": "S"}[v[2]],
                        "vlan_id": vlan_id,
                    })
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        cmd = "debug info"
        r = []
        for match in self.rx_line.finditer(self.cli(cmd)):
            m_interface = match.group("interfaces")
            m_vlan = match.group("vlan_id")
            m_mac = match.group("mac")
            if ((interface is None and vlan is None and mac is None)
                    or (interface is not None and interface == m_interface)
                    or (vlan is not None and vlan == m_vlan)
                    or (mac is not None and mac == m_mac)):
                r += [{
                    "vlan_id": m_vlan,
                    "mac": m_mac,
                    "interfaces": [m_interface],
                    "type": {"Learnt": "D", "Static": "S"}[match.group("type")]
                }]
        return r
