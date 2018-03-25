# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Qtech.QSW2800.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+\S+\s+"
        r"(?P<iface>\S+)", re.MULTILINE)

    def execute_snmp(self, interface=None, vlan=None, mac=None):
        r = []
        # Try SNMP first
        vlan_oid = []
        if mac is not None:
            mac = mac.lower()
        iface_name = {}
        for v in self.snmp.get_tables(
                ["1.3.6.1.2.1.31.1.1.1.1"], bulk=True):
            name = v[1]
            iface_name.update({v[0]: name})

        for v in self.snmp.get_tables(["1.3.6.1.2.1.17.7.1.2.2.1.2"],
                                      bulk=True, max_retries=1):
            vlan_oid.append(v[0])
        # mac iface type
        for v in self.snmp.get_tables(
                ["1.3.6.1.2.1.17.4.3.1.1", "1.3.6.1.2.1.17.4.3.1.2",
                 "1.3.6.1.2.1.17.4.3.1.3"], bulk=True, max_retries=1):
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
            iface = iface_name[str(v[2])]
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
                "type": {"3": "D", "2": "S", "1": "S"}[str(v[3])],
                "vlan_id": vlan_id,
            })
        return r

    def execute_cli(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "show mac-address-table"
        if mac is not None:
            cmd += "address %s" % mac
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for match in self.rx_line.finditer(self.cli(cmd)):
            iface = match.group("iface")
            # found on QSW-3470-10T-AC-POE fw 1.1.5.6
            if match.group("type").lower() == "unknown":
                continue
            m = {
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [iface],
                "type": {
                    "dynamic": "D",
                    "static": "S",
                    "permanent": "S",
                    "self": "C",
                    "secured": "D",
                    "securec": "S",
                }[match.group("type").lower()],
            }
            if iface == 'CPU':
                m["type"] = "C"
            r += [m]
        return r
