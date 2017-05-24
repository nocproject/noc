# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.Comware.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
import re


class Script(BaseScript):
    name = "HP.Comware.get_portchannel"
    interface = IGetPortchannel

    rx_po_members = re.compile(
        r"^(?P<interface>\S+):\s*\n"
        r"^Aggregation Interface: (?P<agg_interface>\S+)", re.MULTILINE)

    def execute(self):
        try:
            v = self.cli("display link-aggregation member-port")
        except self.CLISyntaxError:
            v = self.cli("display link-aggregation verbose")
        r = []
        for match in self.rx_po_members.finditer(v):
            found = False;
            for i in r:
                if i["interface"] == match.group("agg_interface"):
                    i["members"] += [match.group("interface")]
                    found = True
                    break
            if not found:
                r += [{
                    "interface": match.group("agg_interface"),
                    "type": "L",
                    "members": [match.group("interface")]
                }]
        return r
