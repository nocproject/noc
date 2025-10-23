# ---------------------------------------------------------------------
# Ericsson.MINI_LINK.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Ericsson.MINI_LINK.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"^vlan (?P<vlan_id>\d+)\s*\n^ name (?P<name>\S+)\s*\n", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli_clean("show vlan")):
            r += [match.groupdict()]
        return r
