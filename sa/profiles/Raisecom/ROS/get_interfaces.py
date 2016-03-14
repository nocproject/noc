# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Raisecom.ROS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from collections import defaultdict
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.text import ranges_to_list


class Script(BaseScript):
    name = "Raisecom.ROS.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_vlans = re.compile(r"""
        Port:\s(?P<name>\d+)\s*\n
        Administrative\sMode:\s*(?P<adm_mode>.*)\n
        Operational\sMode:\s*(?P<op_mode>.*)\n
        Access\sMode\sVLAN:\s*(?P<untagged_vlan>.*)\n
        Administrative\sAccess\sEgress\sVLANs:\s*(?P<mvr_vlan>.*)\n
        Operational\sAccess\sEgress\sVLANs:\s*(?P<op_eg_vlan>.*)\n
        Trunk\sNative\sMode\sVLAN:\s*(?P<trunk_native_vlan>.*)\n
        Trunk\sNative\sVLAN:\s*(?P<trunk_native_vlan_mode>.*)\n
        Administrative\sTrunk\sAllowed\sVLANs:\s*(?P<adm_trunk_allowed_vlan>.*)\n
        Operational\sTrunk\sAllowed\sVLANs:\s*(?P<op_trunk_allowed_vlan>.*)\n
        Administrative\sTrunk\sUntagged\sVLANs:\s*(?P<adm_trunk_untagged_vlan>.*)\n
        Operational\sTrunk\sUntagged\sVLANs:\s*(?P<op_trunk_untagged_vlan>.*)
        """, re.VERBOSE
                          )

    def parse_vlans(self, section):
        r = {}
        match = re.search(self.rx_vlans, section)
        if match:
            r = match.groupdict()
        return r

    def execute(self):
        ifaces = []
        v = self.cli("show interface port description")
        for line in v.splitlines()[2:-1]:
            i = {
                "name": int(line[:8]),
                "description": str(line[8:]),
                "type": "physical",
                "subinterfaces": []
            }
            ifaces.append(i)

        statuses = []
        v = self.cli("show interface port")
        for line in v.splitlines()[5:]:
            i = {
                "name": int(line[:6]),
                "admin_status": "enable" in line[7:14],
                "oper_status": "up" in line[14:29]
            }
            statuses.append(i)

        vlans = []
        v = self.cli("show interface port switchport")
        for section in v.split("\n\n"):
            if not section:
                continue
            vlans.append(self.parse_vlans(section))

        d = defaultdict(dict)

        for l in (statuses, ifaces):
            for elem in l:
                d[elem['name']].update(elem)
        l3 = d.values()

        for port in l3:
            name = port["name"]
            port["subinterfaces"] = [{
                "name": str(name),
                "enabled_afi": ["BRIDGE"],
                "description": port["description"],
                "tagged_vlans": [],
                "untagged_vlan": [int(vlan['untagged_vlan']) for vlan in vlans if int(vlan['name']) == name][0]
            }]
            tvl = [vlan['op_trunk_allowed_vlan'] for vlan in vlans if int(vlan['name']) == name][0]
            if 'n/a' not in tvl:
                port["subinterfaces"][0]['tagged_vlans'] = ranges_to_list(tvl)


        return [{"interfaces": l3}]

