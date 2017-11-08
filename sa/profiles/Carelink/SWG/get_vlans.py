# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Carelink.SWG.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.lib.text import parse_table
from noc.lib.validators import is_int
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Carelink.SWG.get_vlans"
    interface = IGetVlans
    cache = True

    def execute(self):
        r = []
        for v in parse_table(self.cli("show vlan", cached=True), max_width=80):
            if not is_int(v[0]):
                continue
            vlan_id = v[0]
            descr = v[1]
            r += [{"vlan_id": v[0], "name": v[1]}]
        return r
