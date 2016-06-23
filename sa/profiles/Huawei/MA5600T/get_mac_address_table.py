# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.MA5600T.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re


class Script(BaseScript):
    name = "Huawei.MA5600T.get_mac_address_table"
    interface = IGetMACAddressTable
    TIMEOUT = 240

    rx_line = re.compile(
        r"^\s*(?P<p_type>eth|adl)\s+(?P<mac>\S+)\s+(?P<type>dynamic|static)\s+"
        r"(?P<interfaces>\d+\s*/\d+\s*/\d+)\s+"
        r"(?P<vpi>\d+|\-)\s+(?P<vci>\d+|\-)\s+(?P<vlan_id>\d+)\s*\n",
        re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        ports = self.profile.fill_ports(self)
        for i in range(len(ports)):
            p = 0
            while p <= int(ports[i]["n"]):
                if ports[i]["t"] == "ADSL":
                    v = self.cli("display mac-address adsl 0/%d/%d" % (i, p))
                if ports[i]["t"] == "GE":
                    v = self.cli("display mac-address ethernet 0/%d/%d" % (i, p))
                for match in self.rx_line.finditer(v):
                    r += [{
                        "vlan_id": match.group("vlan_id"),
                        "mac": match.group("mac"),
                        "interfaces": [("0/%d/%d" % (i, p))],
                        "type": {
                            "dynamic":"D",
                            "static":"S"
                        }[match.group("type")]
                    }]
                p += 1
        return r
