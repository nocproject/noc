# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.sa.profiles.DLink.DxS import DES3200
from noc.sa.profiles.DLink.DxS import DES3500
from noc.sa.profiles.DLink.DxS import DGS3120
from noc.sa.profiles.DLink.DxS import DGS3400
from noc.sa.profiles.DLink.DxS import DGS3420
from noc.sa.profiles.DLink.DxS import DGS3600
from noc.sa.profiles.DLink.DxS import DGS3620
import re


class Script(BaseScript):
    name = "DLink.DxS.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(\S+\s+)?"
        r"(?P<mac>[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-"
        r"[0-9A-F]{2}-[0-9A-F]{2})\s+"
        r"(?P<interfaces>\S+)\s+(?P<type>\S+)\s*(\S*\s*)?$", re.MULTILINE)

    def execute_snmp(self, interface=None, vlan=None, mac=None):
        if mac is not None:
            mac = mac.lower()
        iface_name = self.scripts.get_ifindexes()
        # http://www.dlink.ru/ru/faq/59/print_262.html
        # vlan mac iface type
        r = []
        for v in self.snmp.get_tables([
            "1.3.6.1.2.1.17.7.1.2.2.1.2",  # Q-BRIDGE-MIB::dot1qTpFdbPort
            "1.3.6.1.2.1.17.7.1.2.2.1.3"   # Q-BRIDGE-MIB::dot1qTpFdbTable
        ]):
            if v[0]:
                m = ":".join(["%02x" % int(c) for c in v[0].split(".")])
                m = m[m.index(":") + 1:]
                if mac is not None and m != mac:
                    continue
            else:
                continue
            if int(v[2]) < 3:
                continue
            if v[1] == 0:  # 0 port - is a commutator's MAC
                iface = "CPU"
            else:
                iface = iface_name[str(v[1])]
            if interface is not None and iface != interface:
                continue
            vlan_id = int(v[0].split('.')[0])
            if vlan is not None and vlan_id != vlan:
                continue
            r += [{
                "interfaces": [iface],
                "mac": m,
                "type": {
                    # "1": "D",  # Other
                    # "2": "D",  # Invalid
                    "3": "D",  # Learned
                    "4": "C",  # Self
                    "5": "S"   # mgmt
                }[str(v[2])],
                "vlan_id": vlan_id,
            }]
        return r

    def execute_cli(self, interface=None, vlan=None, mac=None):
        cmd = "show fdb"
        if mac is not None:
            cmd += " mac_address %s" % mac
        if interface is not None:
            cmd += " port %s" % interface
        if vlan is not None:
            if (
                self.match_version(DES3200, version__gte="1.33") or
                self.match_version(DGS3120, version__gte="1.00.00") or
                self.match_version(DGS3400, version__gte="2.70") or
                self.match_version(DGS3420, version__gte="1.00.00") or
                self.match_version(DGS3600, version__gte="2.52") or
                self.match_version(DGS3620, version__gte="1.00.00")
            ):
                cmd += " vlanid %d" % vlan
            else:
                if self.match_version(DES3500, version__gte="6.00"):
                    cmd += " vid %d" % vlan
                else:
                    for v in self.scripts.get_vlans():
                        if v["vlan_id"] == vlan:
                            cmd += " vlan %s" % v["name"]
                            break
        r = []
        for match in self.rx_line.finditer(self.cli(cmd)):
            mactype = match.group("type").lower()
            r += [{
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [match.group("interfaces")],
                "type": {
                    "dynamic": "D",
                    "static": "S",
                    "self": "C",
                    "cpu": "C",
                    "asymmetric": "C",
                    "permanent": "S",
                    "drop": "D",
                    "deleteontimeout": "D",
                    "del_on_timeout": "D",
                    "deleteonreset": "D",
                    "del_on_reset": "D",
                    "blockbyaddrbind": "D",
                    "unblockbyaddrbind": "D"}[mactype]
            }]
        return r
