# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.Comware.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "HP.Comware.get_vlans"
    interface = IGetVlans

    def execute(self):
        vlans = self.strip_first_lines(self.cli("display vlan"), 2)
        vlans = vlans.replace("The following VLANs exist:\n", "")
        vlans = vlans.replace("(default)", "")
        vlans = vlans.replace("\n", ",")
        vlans = self.expand_rangelist(vlans)
        r = []
        for v in vlans:
            if int(v) == 1:
                continue
            r += [{
                "vlan_id": int(v),
            }]
        return r
