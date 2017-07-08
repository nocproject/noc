# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# BDCOM.IOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "BDCOM.IOS.get_vlans"
    interface = IGetVlans

    def execute(self):
        r = []
        for i in parse_table(self.cli("show vlan"), allow_wrap=True):
            r += [{
                "vlan_id": i[0],
                "name": i[2]
            }]
        return r
