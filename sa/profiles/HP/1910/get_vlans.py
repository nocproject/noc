# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# HP.1910.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "HP.1910.get_vlans"
    interface = IGetVlans
=======
##----------------------------------------------------------------------
## HP.1910.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "HP.1910.get_vlans"
    implements = [IGetVlans]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_vlan = re.compile(r"^\s*VLAN ID: (?P<vlan>\d+)$")
    rx_name = re.compile(r"^\s*Name: (?P<name>.+)$")

    def execute(self):
        r = []
        # Try snmp first
        """
        # Not working
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
                    r.append({
                        "vlan_id": vlan,
                        "name": name
                        })
                return r
            except self.snmp.TimeOutError:
                pass
        """

        # Fallback to CLI
        vlans = self.cli("display vlan all")
        vlans = vlans.splitlines()
        for i in range(len(vlans)):
            match_v = self.rx_vlan.search(vlans[i])
            if match_v:
                i += 1
                while not self.rx_name.search(vlans[i]):
                    i += 1
                match_n = self.rx_name.search(vlans[i])
                r.append({
                    "vlan_id": int(match_v.group("vlan")),
                    "name": match_n.group("name")
                    })
        return r
