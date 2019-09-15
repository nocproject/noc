# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8100.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.text import parse_table


class Script(BaseScript):
    name = "AlliedTelesis.AT8100.get_vlans"
    interface = IGetVlans

    def execute_cli(self):
        r = []
        v = self.cli("show vlan brief", cached=True)
        t = parse_table(v, allow_wrap=True)
        for i in t:
            r += [{"vlan_id": int(i[0]), "name": i[1]}]
        return r
