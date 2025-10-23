# ---------------------------------------------------------------------
# DLink.DxS_Industrial_CLI.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re


class Script(BaseScript):
    name = "DLink.DxS_Industrial_CLI.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(
        r"^\s*VLAN (?P<vlan_id>\d+)\s*\n^\s*Name\s*:\s+(?P<name>\S+)\s*\n", re.MULTILINE
    )

    def execute(self):
        r = []
        v = self.cli("show vlan", cached=True)
        for match in self.rx_vlan.finditer(v):
            r += [match.groupdict()]
        return r
