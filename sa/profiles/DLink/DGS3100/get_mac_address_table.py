# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DGS3100.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
=======
##----------------------------------------------------------------------
## DLink.DGS3100.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.sa.profiles.DLink.DGS3100 import DGS3100
import re


<<<<<<< HEAD
class Script(BaseScript):
    name = "DLink.DGS3100.get_mac_address_table"
    interface = IGetMACAddressTable
=======
class Script(NOCScript):
    name = "DLink.DGS3100.get_mac_address_table"
    implements = [IGetMACAddressTable]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+\S+\s+(?P<mac>\S+)\s+"
        r"(?P<interfaces>\S+)\s+(?P<type>\S+)\s*(\S*\s*)?$", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        # Try SNMP first
<<<<<<< HEAD
        if self.has_snmp():
=======
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                vlan_oid = []
                if mac is not None:
                    mac = mac.lower()
                for v in self.snmp.get_tables([
                    "1.3.6.1.2.1.17.7.1.2.2.1.2"
                ], bulk=True):
                    vlan_oid.append(v[0])

                # mac iface type
                for v in self.snmp.get_tables([
                    "1.3.6.1.2.1.17.7.1.2.2.1.2",
                    "1.3.6.1.2.1.17.7.1.2.2.1.3"
                ], bulk=True):
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
                    if not v[2] or int(v[2]) > 3 or int(v[2]) < 1:
                        continue
                    iface = self.snmp.get(
<<<<<<< HEAD
                        "1.3.6.1.2.1.31.1.1.1.1." + str(v[1]),
=======
                        "1.3.6.1.2.1.31.1.1.1.1." + v[1],
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
                        "type": {"3": "D", "2": "S", "1": "S"}[str(v[2])],
=======
                        "type": {"3": "D", "2": "S", "1": "S"}[v[2]],
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                        "vlan_id": vlan_id,
                    })
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        cmd = "show fdb"
        if mac is not None:
            cmd += " mac_address %s" % mac
        if interface is not None:
            cmd += " port %s" % interface
        if vlan is not None:
            if self.match_version(DGS3100, version__gte="3.60.30"):
                cmd += " vlanid %d" % vlan
            else:
                for v in self.scripts.get_vlans():
                    if v["vlan_id"] == vlan:
                        cmd += " vlan %s" % v["name"]
                        break
        r = []
        for match in self.rx_line.finditer(self.cli(cmd)):
            r += [{
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [match.group("interfaces")],
                "type": {
                    "dynamic": "D",
                    "static": "S",
                    "deleteontimeout": "D",
                    "deleteonreset": "D",
                    "permanent": "S",
                    "self": "S"
                }[match.group("type").lower()],
            }]
        return r
