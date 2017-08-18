# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES5448.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.MES5448.get_portchannel"
    interface = IGetPortchannel

    TYPES = {
        "Dyn.": "L",
        "Stat": "S"
    }

    def execute(self):
        r = []
        interface = {}
        for i in parse_table(self.cli("show port-channel all")):
            if i[3] == "Up":
                if interface:
                    r += [interface]
                interface = {
                    "interface": i[0],
                    "type": self.TYPES[i[5]],
                    "members": [i[6]]
                }
            elif not i[1] and i[6] and interface:
                interface["members"] += [i[6]]
        if interface:
            r += [interface]
        return r
