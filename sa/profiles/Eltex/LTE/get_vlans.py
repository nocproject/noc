# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTE.get_vlans
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
    name = "Eltex.LTE.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(
        r"^VLAN (?P<vlan_id>\d+)\s+\(name: (?P<name>\S+)\)", re.MULTILINE)

    def execute(self):
        r = []
        with self.profile.switch(self):
            for match in self.rx_vlan.finditer(self.cli("show vlan")):
                r += [match.groupdict()]
        return r
