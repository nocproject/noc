# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IBM.NOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "IBM.NOS.get_vlans"
    interface = IGetVlans
    #
    # Extract vlan information
    #
    rx_vlan_line = re.compile(
        r"^(?P<vlan_id>\d{1,4})\s+(?P<name>.+?)\s+(?:ena|dis)",
        re.MULTILINE)

    def extract_vlans(self, data):
        return [
            {
                "vlan_id": int(match.group("vlan_id")),
                "name": match.group("name")
            }
            for match in self.rx_vlan_line.finditer(data)
        ]

    def execute_cli(self):
        vlans = self.cli("show vlan")
        return self.extract_vlans(vlans)
