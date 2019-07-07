# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Planet.WGSD.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.mib import mib


class Script(BaseScript):
    name = "Planet.WGSD.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<name>.+?)\s+(\S+|)\s+\S+\s+\S+\s*$", re.MULTILINE
    )

    def execute_snmp(self):
        r = []
        for vlan, name in self.snmp.join_tables(
            mib["Q-BRIDGE-MIB::dot1qVlanFdbId"], mib["Q-BRIDGE-MIB::dot1qVlanStaticName"]
        ):
            r.append({"vlan_id": vlan, "name": name})
        return r

    def execute_cli(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            if match.group("name") != "-":
                r += [match.groupdict()]
            else:
                r += [{"vlan_id": int(match.group("vlan_id"))}]
        return r
