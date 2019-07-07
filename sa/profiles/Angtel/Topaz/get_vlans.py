# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Angtel.Topaz.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Angtel.Topaz.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"^\s*(?P<vlan_id>\d+)\s+(?P<name>\S+)", re.MULTILINE)

    def execute_cli(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            r += [match.groupdict()]
        return r
