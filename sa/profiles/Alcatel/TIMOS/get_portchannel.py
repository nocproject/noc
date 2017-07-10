# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.TIMOS.get_portchannel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
import re


class Script(BaseScript):
    name = "Alcatel.TIMOS.get_portchannel"
    interface = IGetPortchannel

    rx_lag = re.compile(
        r"^(?P<number>\d+)\s+up\s+(?P<opr>up|down)\s+",
        re.MULTILINE)
    rx_port = re.compile(
        r"^(\d+\(e\))?\s+(?P<port>\d+/\d+/\d+)\s+(?P<adm>up|down)",
        re.MULTILINE)

    def execute(self):
        try:
            v = self.cli("show lag")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        for match in self.rx_lag.finditer(v):
            i = {
                "interface": "lag-%s" % match.group("number"),
                "members": [],
                "type": "L"
            }
            c = self.cli("show lag %s port" % match.group("number"))
            for match1 in self.rx_port.finditer(c):
                i["members"] += [match1.group("port")]
            r += [i]
        return r
