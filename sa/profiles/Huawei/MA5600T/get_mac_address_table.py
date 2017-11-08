# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Huawei.MA5600T.get_mac_address_table"
    interface = IGetMACAddressTable
    TIMEOUT = 240

    rx_line = re.compile(
        r"^\s*.*(?P<p_type>eth|adl|gpon)\s+(?P<mac>\S+)\s+"
        r"(?P<type>dynamic|static)\s+"
        r"(?P<interfaces>\d+\s*/\d+\s*/\d+)\s+"
        r"(?P<vpi>\d+|\-)\s+(?P<vci>\d+|\-)\s+"
        r"((?P<FLOWTYPE>\d+|\-)\s+(?P<FLOWPARA>\d+|\-)\s+)?(?P<vlan_id>\d+)\s*\n",
        re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        ports = self.profile.fill_ports(self)
        adsl_port = "adsl"
        vdsl_port = "port"  # Need more examples
        gpon_port = "gpon"
        ethernet_port = "ethernet"
        for i in range(len(ports)):
            p = 0
            while p <= int(ports[i]["n"]):
                if not ports[i]["s"][p]:
                    # Skip not running interface
                    p += 1
                    continue
                if (ports[i]["t"] == "ADSL"):
                    try:
                        v = self.cli("display mac-address %s 0/%d/%d" % (adsl_port, i, p))
                    except self.CLISyntaxError:
                        v = self.cli("display mac-address port 0/%d/%d" % (i, p))
                        adsl_port = "port"
                if (ports[i]["t"] == "VDSL"):
                    try:
                        v = self.cli("display mac-address %s 0/%d/%d" % (vdsl_port, i, p))
                    except self.CLISyntaxError:
                        v = self.cli("display mac-address port 0/%d/%d" % (i, p))
                        vdsl_port = "port"
                if (ports[i]["t"] == "GPON"):
                    try:
                        v = self.cli("display mac-address %s 0/%d/%d" % (gpon_port, i, p))
                    except self.CLISyntaxError:
                        v = self.cli("display mac-address port 0/%d/%d" % (i, p))
                        gpon_port = "port"
                if (ports[i]["t"] in ["10GE", "GE", "FE"]):
                    try:
                        v = self.cli("display mac-address %s 0/%d/%d" % (ethernet_port, i, p))
                    except self.CLISyntaxError:
                        v = self.cli("display mac-address port 0/%d/%d" % (i, p))
                        ethernet_port = "port"
                for match in self.rx_line.finditer(v):
                    r += [{
                        "vlan_id": match.group("vlan_id"),
                        "mac": match.group("mac"),
                        "interfaces": [("0/%d/%d" % (i, p))],
                        "type": {
                            "dynamic": "D",
                            "static": "S"
                        }[match.group("type")]
                    }]
                p += 1
        return r
