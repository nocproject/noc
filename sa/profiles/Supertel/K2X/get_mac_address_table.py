# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_mac_address_table
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
    name = "Supertel.K2X.get_mac_address_table"
    implements = [IGetMACAddressTable]

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+"
        r"(?P<interfaces>\S+)\s+(?P<type>\S+)\s*$",
        re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        # Try SNMP first
        if self.has_snmp():
            try:
                vlan_oid = []
                if mac is not None:
                    mac = mac.lower()
                iface_name = {}
                for v in self.snmp.get_tables(["1.3.6.1.2.1.31.1.1.1.1"],
                                              bulk=True):
                    if v[1][:1] == 'g' or v[1][:2] == 'ch':
                        name = v[1]
                        iface_name.update({v[0]: name})

                for v in self.snmp.get_tables(["1.3.6.1.2.1.17.7.1.2.2.1.2"],
                                              bulk=True):
                    vlan_oid.append(v[0])
                # mac iface type
                for v in self.snmp.get_tables(["1.3.6.1.2.1.17.4.3.1.1",
                                               "1.3.6.1.2.1.17.4.3.1.2",
                                               "1.3.6.1.2.1.17.4.3.1.3"],
                                              bulk=True):
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

        # Fallback to CLI
        cmd = "show bridge address-table"
        if vlan is not None:
            cmd += " vlan %s" % vlan
        if interface is not None:
            if interface[:1] == 'g':
                cmd += " ethernet %s" % interface
            elif interface[:2] == 'ch':
                cmd += " port-channel %s" % interface
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        for match in self.rx_line.finditer(self.cli(cmd)):
                interfaces = match.group("interfaces")
                if interfaces == '0':
                    continue
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [interfaces],
                    "type": {
                        "dynamic": "D",
                        "static": "S",
                        "permanent": "S",
                        "self": "S"
                        }[match.group("type").lower()],
                    })
        return r
