# ---------------------------------------------------------------------
# EdgeCore.ES.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import operator

# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "EdgeCore.ES.get_vlans"
    cache = True
    interface = IGetVlans

    rx_vlan_line_4626 = re.compile(r"^\s*(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s+", re.MULTILINE)
    rx_vlan_line_4612 = re.compile(
        r"^\s*(?P<vlan_id>\d{1,4})\s+\S+\s+(?P<name>\S+)\s+", re.MULTILINE
    )
    rx_vlan_line_3526 = re.compile(
        r"^VLAN ID\s*?:\s+?(?P<vlan_id>\d{1,4})\n"
        r"^Type\s*:.*\n"
        r"^Name\s*?:\s+(?P<name>\S*?)\n",
        re.MULTILINE,
    )

    def execute_snmp(self):
        # Get VLAN names
        result = []
        for oid, v in self.snmp.getnext(
            "1.3.6.1.2.1.17.7.1.4.3.1.1", bulk=True
        ):  # dot1qVlanStaticName
            o = oid.split(".")[-1]
            result += [{"vlan_id": int(o), "name": v.strip().rstrip(smart_text("\x00"))}]
        return sorted(result, key=operator.itemgetter("vlan_id"))

    def execute_cli(self):
        r = []
        vlans = self.cli("show vlan")
        # ES4626 = Cisco Style
        if self.is_platform_4626:
            for match in self.rx_vlan_line_4626.finditer(vlans):
                r += [match.groupdict()]
            return r

        # ES4612 or 3526S
        if self.is_platform_4612 or self.is_platform_3526s:
            for match in self.rx_vlan_line_4612.finditer(vlans):
                r += [match.groupdict()]
            return r

        # Other
        for match in self.rx_vlan_line_3526.finditer(vlans):
            if match.group("name"):
                r += [match.groupdict()]
            else:
                r += [{"vlan_id": int(match.group("vlan_id"))}]
        return r
