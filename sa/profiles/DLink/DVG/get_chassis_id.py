# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DVG.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mib import mib


class Script(BaseScript):
    name = "DLink.DVG.get_chassis_id"
    interface = IGetChassisID
    # Always try SNMP first
    always_prefer = "S"

    rx_mac1 = re.compile(r"^WAN MAC \[+(?P<mac>\S+)+\]$", re.MULTILINE)
    rx_mac2 = re.compile(r"Link encap:Ethernet\s+HWaddr (?P<mac>\S+)")
    SNMP_GET_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress", 2]]}

    def execute_cli(self):
        r = self.cli("GET STATUS WAN", cached=True)
        match = self.rx_mac1.search(r)
        if match:
            return [
                {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
            ]

        r = self.cli("ifconfig", cached=True)
        macs = set()
        for k in self.rx_mac2.findall(r):
            try:
                macs.add(k)
            except ValueError:
                pass
        if macs:
            macs = list(macs)
            macs.sort()
            return [
                {"first_chassis_mac": f, "last_chassis_mac": t}
                for f, t in self.macs_to_ranges(macs)
            ]

        raise self.NotSupportedError()
