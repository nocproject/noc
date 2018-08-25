# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cambium.ePMP.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Cambium.ePMP.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute_cli(self, **kwargs):
        # Replace # with @ to prevent prompt matching
        r = {}
        v = self.cli("show dashboard", cached=True).strip()
        ee = [l.strip().split(" ", 1) for l in v.splitlines()]
        for e in ee:
            if len(e) == 2:
                r[e[0]] = e[1].strip()
            else:
                r[e[0]] = None
        if r["cambiumConnectedAPMACAddress"]:
            return {
                "first_chassis_mac": r["cambiumConnectedAPMACAddress"],
                "last_chassis_mac": r["cambiumConnectedAPMACAddress"]
            }
