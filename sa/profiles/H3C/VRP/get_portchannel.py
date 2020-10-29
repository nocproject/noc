# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# H3C.VRP.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# PYTHON modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "H3C.VRP.get_portchannel"
    interface = IGetPortchannel

    rx_po_members = re.compile(
        r"^(?P<interface>\S+):\s*\n"
        r"^Aggregation Interface: (?P<agg_interface>\S+)\n"
        r"^(?P<is_dynamic>Local:)?",
        re.MULTILINE,
    )

    def execute(self):
        r, s = [], ""
        try:
            s = self.cli("display link-aggregation member-port")
            if "No link-aggregation" in r or "No link aggregation" in r:
                return []
        except self.CLISyntaxError:
            return []

        for match in self.rx_po_members.finditer(s):
            found = False
            for i in r:
                if i["interface"] == match.group("agg_interface"):
                    i["members"] += [match.group("interface")]
                    found = True
                    break
            if not found:
                r += [
                    {
                        "interface": match.group("agg_interface"),
                        "type": "L" if match.group("is_dynamic") else "S",
                        "members": [match.group("interface")],
                    }
                ]
        return r
