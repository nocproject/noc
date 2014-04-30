# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable
from noc.sa.profiles.DLink.DxS import DES3200
from noc.sa.profiles.DLink.DxS import DGS3120
from noc.sa.profiles.DLink.DxS import DGS3400
from noc.sa.profiles.DLink.DxS import DGS3420
from noc.sa.profiles.DLink.DxS import DGS3600
from noc.sa.profiles.DLink.DxS import DGS3620
import re


class Script(NOCScript):
    name = "DLink.DxS.get_mac_address_table"
    implements = [IGetMACAddressTable]
    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(\S+\s+)?"
        r"(?P<mac>[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-"
        r"[0-9A-F]{2}-[0-9A-F]{2})\s+"
        r"(?P<interfaces>\S+)\s+(?P<type>\S+)\s*(\S*\s*)?$", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show fdb"
        if mac is not None:
            cmd += " mac_address %s" % mac
        if interface is not None:
            cmd += " port %s" % interface
        if vlan is not None:
            if self.match_version(DES3200, version__gte="1.33") \
            or self.match_version(DGS3120, version__gte="1.00.00") \
            or self.match_version(DGS3400, version__gte="2.70") \
            or self.match_version(DGS3420, version__gte="1.00.00") \
            or self.match_version(DGS3600, version__gte="2.52") \
            or self.match_version(DGS3620, version__gte="1.00.00"):
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
                    "dynamic":"D",
                    "static":"S",
                    "self":"S",
                    "permanent":"S",
                    "deleteontimeout":"D",
                    "del_on_timeout":"D",
                    "deleteonreset":"D",
                    "del_on_reset":"D",
                    "blockbyaddrbind":"D"}[mactype]
            }]
        return r
