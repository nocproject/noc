# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ericsson.BSC.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Ericsson.BSC.get_interfaces"
    cache = True
    interface = IGetInterfaces

    def execute(self):
        interfaces = []
        with self.profile.mml(self):
            v = self.cli("RXMOP:MOTY=RXOTG;")
            for i in self.profile.iter_items(v):
                description = i["RSITE"]
                mo = i["MO"]
                ifname = mo.split("-")[1]
                print ifname
                interfaces += [{
                    "type": "physical",
                    "name": ifname,
                    "description": description,
                    "subinterfaces": [{
                        "name": ifname,
                        "description": description,
                        "enabled_afi": ["BRIDGE"]
                    }]
                }]
            return [{"interfaces": interfaces}]
