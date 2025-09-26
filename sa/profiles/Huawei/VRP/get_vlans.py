# ---------------------------------------------------------------------
# Huawei.VRP.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.mib import mib
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "Huawei.VRP.get_vlans"
    interface = IGetVlans

    def execute_snmp(self, **kwargs):
        result = []
        oids = {}
        # Get OID -> VLAN ID mapping
        # dot1qVlanFdbId
        for oid, v in self.snmp.getnext(mib["Q-BRIDGE-MIB::dot1qVlanFdbId"]):
            oids[oid.split(".")[-1]] = v
        if oids:
            # Get VLAN names
            # dot1qVlanStaticName
            for oid, v in self.snmp.getnext(mib["Q-BRIDGE-MIB::dot1qVlanStaticName"]):
                o = oid.split(".")[-1]
                result += [{"vlan_id": int(oids[o]), "name": v.strip().rstrip(smart_text("\x00"))}]
        else:
            tmp_vlan = []
            # dot1qVlanStaticName
            for oid, v in self.snmp.getnext(mib["Q-BRIDGE-MIB::dot1qVlanStaticEntry"]):
                vlan_id = int(oid.split(".")[-1])
                if vlan_id in tmp_vlan:
                    break
                result += [{"vlan_id": vlan_id, "name": v.strip().rstrip(smart_text("\x00"))}]
                tmp_vlan += [vlan_id]
        if result:
            return sorted(result, key=lambda x: x["vlan_id"])
        raise self.NotSupportedError()

    def execute_cli(self):
        # Try CLI
        rx_vlan_line_vrp5 = re.compile(
            r"^(?P<vlan_id>\d{1,4})\s*?.*?", re.IGNORECASE | re.DOTALL | re.MULTILINE
        )
        rx_vlan_line_vrp3 = re.compile(
            r"^\sVLAN ID:\s+?(?P<vlan_id>\d{1,4})\n.*?"
            r"(?:Name|Description):\s+(?P<name>.*?)\n"
            r".*?(\n\n|$)",
            re.IGNORECASE | re.DOTALL | re.MULTILINE,
        )

        if self.is_kernelgte_5:
            vlans = self.cli("display vlan", cached=True)
            return [
                {"vlan_id": int(match.group("vlan_id"))}
                for match in rx_vlan_line_vrp5.finditer(vlans)
            ]
        vlans = self.cli("display vlan all", cached=True)
        return [
            {"vlan_id": int(match.group("vlan_id")), "name": match.group("name")}
            for match in rx_vlan_line_vrp3.finditer(vlans)
        ]
