# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS_EE.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.interfaces import IGetVlans
from noc.sa.script import Script as NOCScript


class Script(NOCScript):
    name = "Zyxel.ZyNOS_EE.get_vlans"
    implements = [IGetVlans]
    rx_vlan = re.compile(r"^\s+\d+\s+(?P<vlanname>\S+)\s+(?P<vlanid>\S+).",
                         re.MULTILINE | re.DOTALL)

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                r = []
                for vid, name in self.snmp.join_tables(
                    "1.3.6.1.2.1.17.7.1.4.2.1.3", "1.3.6.1.2.1.17.7.1.4.3.1.1",
                    bulk=True):
                    r += [{"vlan_id": vid, "name": name}]
                return r
            except self.snmp.TimeOutError:
                pass
        r = []
        svlan = self.cli("sys sw vlan1q svlan list")
        for match in self.rx_vlan.finditer(svlan):
            r += [{
                "vlan_id": int(match.group('vlanid')),
                "name":match.group('vlanname')
                }]
        return r
