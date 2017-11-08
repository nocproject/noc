# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# BDCOM.IOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.lib.text import parse_table
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "BDCOM.IOS.get_vlans"
    interface = IGetVlans
    cache = True

    def execute(self):
        r = []
        c = self.cli("show vlan", cached=True)
        for i in parse_table(c, allow_wrap=True, n_row_delim=","):
            r += [{
                "vlan_id": i[0],
                "name": i[2]
            }]
        return r
