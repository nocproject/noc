# ---------------------------------------------------------------------
# Eltex.LTE.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.LTE.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"^VLAN (?P<vlan_id>\d+)\s+\(name: (?P<name>\S+)\)", re.MULTILINE)

    def execute(self):
        r = []
        with self.profile.switch(self):
            c = self.cli("show vlan", cached=True)
            for match in self.rx_vlan.finditer(c):
                r += [match.groupdict()]
            if not r:
                t = parse_table(c, allow_wrap=True, footer="dummy footer")
                for i in t:
                    r += [{"vlan_id": i[0], "name": i[1]}]
        return r
