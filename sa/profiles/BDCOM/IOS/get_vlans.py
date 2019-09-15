# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# BDCOM.IOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.text import parse_table


class Script(BaseScript):
    name = "BDCOM.IOS.get_vlans"
    interface = IGetVlans
    cache = True

    def execute(self):
        r = []
        c = self.cli("show vlan", cached=True)
        for i in parse_table(c, allow_wrap=True, n_row_delim=","):
            r += [{"vlan_id": i[0], "name": i[2]}]
        return r
