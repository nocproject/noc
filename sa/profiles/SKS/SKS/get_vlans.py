# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.text import parse_table


class Script(BaseScript):
    name = "SKS.SKS.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"^\s*(?P<vlan_id>\d+)\s+(?P<name>\S+)", re.MULTILINE)
    rx_status = re.compile(r"VLAN\s+Status\s+Name\s+Ports", re.MULTILINE)

    def execute_cli(self):
        r = []
        c = self.cli("show vlan")
        if bool(self.rx_status.search(c)):
            t = parse_table(c, allow_wrap=True)
            for i in t:
                r += [{"vlan_id": i[0], "name": i[2]}]
        else:
            for match in self.rx_vlan.finditer(c):
                r += [match.groupdict()]
        return r
