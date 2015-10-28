# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1910.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "HP.1910.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>\S+)\s+(?P<interfaces>\S+)\s+\S+$",
        re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        # Try SNMP first
        """
        # No mac adresses....
        if self.has_snmp():
            try:
                vlan_oid = []
                if mac is not None:
                    mac = mac.lower()

                # Get switchport index and name
                iface_name = {}
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.31.1.1.1.1"], bulk=True):
                    iface = v[1].replace('GigabitEthernet', 'Gi ')
                    iface = iface.replace('Bridge-Aggregation', 'Po ')
                    iface_name.update({v[0]: iface})

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
                    iface = iface_name[v[2]]
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
        """

        # Fallback to CLI
        cmd = "display mac-address"
        if mac is not None:
            mac = self.profile.convert_mac(mac)
            mac = mac.replace(':', '')
            mac = mac[0:4] + '-' + mac[4:8] + '-' + mac[8:]
            cmd += " %s" % mac
        if interface is not None:
            interface = interface.replace('Po ', 'Bridge-Aggregation')
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for match in self.rx_line.finditer(self.cli(cmd)):
                iface = match.group("interfaces")
                iface = iface.replace('GigabitEthernet', 'Gi ')
                iface = iface.replace('Bridge-Aggregation', 'Po ')
                if iface == '0':
                    continue
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [iface],
                    "type": {
                        "learned": "D",
                        "static": "S",
                        "permanent": "S",
                        "self": "S"
                        }[match.group("type").lower()],
                    })
        return r
