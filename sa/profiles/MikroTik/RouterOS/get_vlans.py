# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "MikroTik.RouterOS.get_vlans"
    implements = [IGetVlans]
    rx_vlan = re.compile(
        r"vlan-id=(?P<vlanid>\d+) ports=", re.MULTILINE | re.DOTALL)

    def execute(self):
        try:
            v = self.cli("interface ethernet switch vlan print terse")
            v = self.cli("interface ethernet switch vlan print terse")
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        r = []
        for match in self.rx_vlan.finditer(v):
            vlan = match.group('vlanid')
            r.append({"vlan_id": int(vlan)})
        return r
