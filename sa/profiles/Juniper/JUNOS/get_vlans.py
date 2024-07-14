# ---------------------------------------------------------------------
# Juniper.JUNOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_vlans import Script as BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Juniper.JUNOS.get_vlans"
    interface = IGetVlans

    rx_vlan_line = re.compile(
        r"^((?P<routing_instance>\S+)\s+)?(?P<name>\S+)\s+(?P<vlan_id>[1-9][0-9]*)\s+", re.MULTILINE
    )

    def execute_cli(self):
        if not self.is_switch or not self.profile.command_exist(self, "vlans"):
            return []
        r = []
        v = self.cli("show vlans brief")
        for match in self.rx_vlan_line.finditer(v):
            r += [match.groupdict()]
        return r
