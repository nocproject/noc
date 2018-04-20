# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Linksys.SPS2xx.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Linksys.SPS2xx.get_vlans"
    interface = IGetVlans
=======
##----------------------------------------------------------------------
## Linksys.SPS2xx.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "Linksys.SPS2xx.get_vlans"
    implements = [IGetVlans]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_vlan = re.compile(
        r"^\s*(?P<vlan>\d+)\s+(?P<name>.+?)\s+\S+\s+\S+\s+\S", re.MULTILINE)

    def execute(self):
        r = []
        # Try snmp first
<<<<<<< HEAD
        if self.has_snmp():
            try:
                for vlan, name in self.snmp.join_tables(
                        "1.3.6.1.2.1.17.7.1.4.2.1.3",
                        "1.3.6.1.2.1.17.7.1.4.3.1.1"):
=======
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for vlan, name in self.snmp.join_tables(
                    "1.3.6.1.2.1.17.7.1.4.2.1.3", "1.3.6.1.2.1.17.7.1.4.3.1.1",
                    bulk=True):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    r += [{"vlan_id": vlan, "name": name}]
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            r += [{
                "vlan_id": int(match.group("vlan")),
                "name": match.group("name")
            }]
        return r
