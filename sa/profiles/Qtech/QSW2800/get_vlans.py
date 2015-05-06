# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW2800.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "Qtech.QSW2800.get_vlans"
    implements = [IGetVlans]

    rx_vlan = re.compile(r"^(?P<vlanid>\d+)\s+(?P<name>\S+)\s+.+",
                        re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            vlan_id = int(match.group('vlanid'))
            name = match.group('name')
            r += [{
                "vlan_id": vlan_id,
                "name": name
            }]
        return r
