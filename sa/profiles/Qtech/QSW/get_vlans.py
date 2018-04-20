# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Qtech.QSW.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Qtech.QSW.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(
        r"^(?:VLAN name\s+:\s*(?P<name>\S+).|)"
        r"VLAN ID\s+:\s*(?P<vlan_id>\d+)$",
        re.DOTALL | re.MULTILINE)
    rx_vlan1 = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<name>\S+)\s+(?:Static|Dynamic)\s+ENET",
=======
##----------------------------------------------------------------------
## Qtech.QSW.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "Qtech.QSW.get_vlans"
    implements = [IGetVlans]

    rx_vlan = re.compile(
        r"^(VLAN name\s+:\s*(?P<vlanname>\S+).|)"
        r"VLAN ID\s+:\s*(?P<vlanid>\d+)$",
        re.DOTALL | re.MULTILINE)

    rx_vlan1 = re.compile(
        r"^(?P<vlanid>\d+)\s+(?P<vlanname>\S+)\s+(Static|Dynamic)\s+ENET",
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        re.DOTALL | re.MULTILINE)

    def execute(self):
        r = []
        # Try snmp first

        """
        # SNMP Not working!
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
                    if name == "":
                        name = "Vlan-" + vlan
                    r.append({
                        "vlan_id": vlan,
                        "name": name
                        })
                return r
            except self.snmp.TimeOutError:
                pass
        """

        # Fallback to CLI
        v = self.cli("show vlan")
        for match in self.rx_vlan.finditer(v):
<<<<<<< HEAD
            vlan_id = match.group('vlan_id')
            name = match.group('name')
=======
            vlan_id = match.group('vlanid')
            name = match.group('vlanname')
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            if not name:
                r.append({
                    "vlan_id": int(vlan_id)
                })
            else:
<<<<<<< HEAD
                r += [match.groupdict()]
        if r == []:
            for match in self.rx_vlan1.finditer(v):
                vlan_id = match.group('vlan_id')
                name = match.group('name')
=======
                r.append({
                    "vlan_id": int(vlan_id),
                    "name": name
                })
        if r == []:
            for match in self.rx_vlan1.finditer(v):
                vlan_id = match.group('vlanid')
                name = match.group('vlanname')
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                if not name:
                    r.append({
                        "vlan_id": int(vlan_id)
                    })
                else:
<<<<<<< HEAD
                    r += [match.groupdict()]
=======
                    r.append({
                        "vlan_id": int(vlan_id),
                        "name": name
                    })
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

        return r
