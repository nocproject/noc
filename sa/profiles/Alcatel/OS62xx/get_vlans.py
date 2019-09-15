# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.OS62xx.get_vlans
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Alcatel.OS62xx.get_vlans"
    interface = IGetVlans

    def execute(self):
        vlans = self.cli("show vlan")
        r = []
        for v in parse_table(vlans, allow_wrap=True):
            r += [{"vlan_id": int(v[0]), "name": v[1]}]
        return r
