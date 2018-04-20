# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Huawei.VRP.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Huawei.VRP.get_vlans"
    interface = IGetVlans

    def execute(self):
        if self.has_snmp():
            # Try SNMP first
            try:
                result = []
                oids = {}
                # Get OID -> VLAN ID mapping
                # dot1qVlanFdbId
                for oid, v in self.snmp.getnext("1.3.6.1.2.1.17.7.1.4.2.1.3"):
                    oids[oid.split(".")[-1]] = v
                if oids:
                    # Get VLAN names
                    # dot1qVlanStaticName
                    for oid, v in self.snmp.getnext("1.3.6.1.2.1.17.7.1.4.3.1.1"):
                        o = oid.split(".")[-1]
                        result += [{
                            "vlan_id":int(oids[o]),
                            "name":v.strip().rstrip('\x00')
                        }]
                else:
                    tmp_vlan = []
                    # dot1qVlanStaticName
                    for oid, v in self.snmp.getnext("1.3.6.1.2.1.17.7.1.4.3.1"):
                        vlan_id = int(oid.split(".")[-1])
                        if vlan_id in tmp_vlan:
                            break
                        result += [{
                            "vlan_id": vlan_id,
                            "name": v.strip().rstrip('\x00')
                        }]
                        tmp_vlan += [vlan_id]
                if result:
                    return sorted(
                        result, lambda x, y: cmp(x["vlan_id"], y["vlan_id"])
                    )
                else:
                    pass
=======
##----------------------------------------------------------------------
## Huawei.VRP.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC Modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "Huawei.VRP.get_vlans"
    implements = [IGetVlans]

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            # Try SNMP first
            try:
                oids = {}
                # Get OID -> VLAN ID mapping
                for oid, v in self.snmp.getnext("1.3.6.1.2.1.17.7.1.4.2.1.3",
                    bulk=True):  # dot1qVlanFdbId
                    oids[oid.split(".")[-1]] = v
                # Get VLAN names
                result = []
                for oid, v in self.snmp.getnext("1.3.6.1.2.1.17.7.1.4.3.1.1",
                    bulk=True):  # dot1qVlanStaticName
                    o = oid.split(".")[-1]
                    result += [{
                        "vlan_id":int(oids[o]),
                        "name":v.strip().rstrip('\x00')
                    }]
                return sorted(
                    result, lambda x, y: cmp(x["vlan_id"], y["vlan_id"])
                )
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            except self.snmp.TimeOutError:
                # SNMP failed, continue with CLI
                pass
        # Try CLI
        rx_vlan_line_vrp5 = re.compile(
            r"^(?P<vlan_id>\d{1,4})\s*?.*?",
            re.IGNORECASE | re.DOTALL | re.MULTILINE)
        rx_vlan_line_vrp3 = re.compile(
<<<<<<< HEAD
            r"^\sVLAN ID:\s+?(?P<vlan_id>\d{1,4})\n.*?"
            r"(?:Name|Description):\s+(?P<name>.*?)\n"
            r".*?(\n\n|$)", re.IGNORECASE | re.DOTALL | re.MULTILINE)
        version = self.profile.fix_version(self.scripts.get_version())
        if self.match_version(version__gte="5.0"):
=======
            r"^\sVLAN ID:\s+?(?P<vlan_id>\d{1,4})\n.*?Name:\s+(?P<name>.*?)\n"
            r".*?(\n\n|$)", re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if self.match_version(version__startswith="5."):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            vlans = self.cli("display vlan", cached=True)
            return [{
                "vlan_id": int(match.group("vlan_id"))
            } for match in rx_vlan_line_vrp5.finditer(vlans)]
        else:
            vlans = self.cli("display vlan all", cached=True)
            return [{
                "vlan_id": int(match.group("vlan_id")),
                "name": match.group("name")
            } for match in rx_vlan_line_vrp3.finditer(vlans)]
