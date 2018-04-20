# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Zyxel.ZyNOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

# Python modules
import re
# NOC modules
<<<<<<< HEAD
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.script.base import BaseScript


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_vlans"
    interface = IGetVlans
=======
from noc.sa.interfaces import IGetVlans
from noc.sa.script import Script as NOCScript


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_vlans"
    implements = [IGetVlans]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_vlan = re.compile(r"^\s*\d+\s+(?P<vlan_id>\d+)\s+.*$",
                re.MULTILINE)
    rx_vlan_name = re.compile(r"^\s+Name\s+:(?P<name>.*)$",
                re.MULTILINE)

    def execute(self):
<<<<<<< HEAD
        if self.has_snmp():
            try:
                r = []
                for i, vid, name in self.snmp.join([
                    "1.3.6.1.2.1.17.7.1.4.2.1.3",
                    "1.3.6.1.2.1.17.7.1.4.3.1.1"
                ]):
                    if name is not None:
                        r += [{"vlan_id": vid, "name": name}]
                    else:
                        r += [{"vlan_id": vid}]
=======
        if self.snmp and self.access_profile.snmp_ro:
            try:
                r = []
                for vid, name in self.snmp.join_tables(
                                        "1.3.6.1.2.1.17.7.1.4.2.1.3",
                                        "1.3.6.1.2.1.17.7.1.4.3.1.1",
                                        bulk=True):
                    r += [{"vlan_id": vid, "name": name}]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                return r
            except self.snmp.TimeOutError:
                pass

        vlans = self.cli("show vlan")
        r = []
        for match in self.rx_vlan.finditer(vlans):
            vid = int(match.group("vlan_id"))
            vn = self.cli("show vlan %d" % vid)
            match_name = self.re_search(self.rx_vlan_name, vn)
            name = match_name.group("name")
            if name != "":
                r += [{
                    "vlan_id": vid,
                    "name": name
                }]
            else:
                r += [{
                    "vlan_id": vid
                }]
        return r
