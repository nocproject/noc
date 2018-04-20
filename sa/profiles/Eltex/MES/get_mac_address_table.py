# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Eltex.MES.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import print_function
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Eltex.MES.get_mac_address_table"
    interface = IGetMACAddressTable
=======
##----------------------------------------------------------------------
## Eltex.MES.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable


class Script(noc.sa.script.Script):
    name = "Eltex.MES.get_mac_address_table"
    implements = [IGetMACAddressTable]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interfaces>\S+)\s+(?P<type>\S+)",
        re.MULTILINE)

<<<<<<< HEAD
    def execute_snmp(self, interface=None, vlan=None, mac=None):
        r = []
        # Try SNMP first
        vlan_oid = []
        if mac is not None:
            mac = mac.lower()
        iface_name = {}
        for v in self.snmp.get_tables(["1.3.6.1.2.1.31.1.1.1.1"]):
            if v[1][:2] == 'fa' or v[1][:2] == 'gi' or v[1][:2] == 'te' or v[1][:2] == 'po':
                name = v[1]
                name = name.replace('fa', 'Fa ')
                name = name.replace('gi', 'Gi ')
                name = name.replace('te', 'Te ')
                name = name.replace('po', 'Po ')
                iface_name.update({v[0]: name})

        for v in self.snmp.get_tables(["1.3.6.1.2.1.17.7.1.2.2.1.2"]):
            vlan_oid.append(v[0])
        # mac iface type
        for v in self.snmp.get_tables(
                ["1.3.6.1.2.1.17.4.3.1.1",
                 "1.3.6.1.2.1.17.4.3.1.2",
                 "1.3.6.1.2.1.17.4.3.1.3"]):
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
=======
    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                vlan_oid = []
                if mac is not None:
                    mac = mac.lower()
                iface_name = {}
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.31.1.1.1.1"], bulk=True):
                    if v[1][:2] == 'fa' or v[1][:2] == 'gi' or v[1][:2] == 'te' or v[1][:2] == 'po':
                        name = v[1]
                        name = name.replace('fa', 'Fa ')
                        name = name.replace('gi', 'Gi ')
                        name = name.replace('te', 'Te ')
                        name = name.replace('po', 'Po ')
                        iface_name.update({v[0]: name})

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
 
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Fallback to CLI
        cmd = "show mac address-table"
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for match in self.rx_line.finditer(self.cli(cmd)):
<<<<<<< HEAD
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
                    "secure": "S",
                    "permanent": "S",
                    "self": "C"
                }[match.group("type").lower()],
            })
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return r
