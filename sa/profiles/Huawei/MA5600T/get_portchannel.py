# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "Huawei.MA5600T.get_portchannel"
    interface = IGetPortchannel

    rx_id = re.compile("^\s+(?P<id>\d+)\s+\d+", re.MULTILINE)
    rx_iface = re.compile(
        "^\s+(?:Master|Sub) Port: (?P<port>\S+)", re.MULTILINE)

    def execute(self):
        r = []
        try:
            s = self.cli("display lacp link-aggregation summary")
        except self.CLISyntaxError:
            return []
        for match in self.rx_id.finditer(s):
            lid = match.group("id")
            c = self.cli("display lacp link-aggregation verbose %s" % lid)
            iface = {
                "interface": lid,
                "type": "L",
                "members": []
            }
            for match1 in self.rx_iface.finditer(c):
                iface["members"] += [match1.group("port")]
            r += [iface]
        return r
