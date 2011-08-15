# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.interfaces import IGetVlans
from noc.sa.script import Script as NOCScript


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_vlans"
    implements = [IGetVlans]
    rx_vlan = re.compile(r"^\s*\d+\s+(?P<vlan_id>\d+)\s+.*$",
                re.MULTILINE)
    rx_vlan_name = re.compile(r"^\s+Name\s+:(?P<name>.*)$",
                re.MULTILINE)

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                r = []
                for vid, name in self.snmp.join_tables("1.3.6.1.2.1.17.7.1.4.2.1.3",
                                                       "1.3.6.1.2.1.17.7.1.4.3.1.1",
                                                        bulk=True):
                    r += [{"vlan_id": vid, "name": name}]
                return r
            except self.snmp.TimeOutError:
                pass
        vlans = self.cli("show vlan")
        r = []
        for match in self.rx_vlan.finditer(vlans):
            vid = int(match.group("vlan_id"))
            vn = self.cli("show vlan %d" % vid)
            match_name = self.re_search(self.rx_vlan_name, vn)
            r += [{
                "vlan_id": vid,
                "name": match_name.group("name") if match_name.group("name") != "" else ("vlan%s" % vid)
            }]
        return r
