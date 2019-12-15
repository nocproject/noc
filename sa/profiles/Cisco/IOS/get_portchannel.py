# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

# NOC modules
from noc.sa.profiles.Generic.get_portchannel import Script as BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Cisco.IOS.get_portchannel"
    interface = IGetPortchannel

    rx_iface = re.compile(r"^(\S+)\(", re.MULTILINE)

    def extract_iface(self, i):
        match = self.rx_iface.search(i)
        return match.group(1)

    def execute_cli(self):
        r = []
        try:
            s = self.cli("show etherchannel summary")
        except self.CLISyntaxError:
            # Some ASR100X do not have this command
            # raise self.NotSupportedError
            return []
        for i in parse_table(s, allow_wrap=True, max_width=120):
            iface = {"interface": self.extract_iface(i[1]), "members": []}
            if (len(i) == 4) and (i[2] == "LACP"):
                iface["type"] = "L"
            else:
                iface["type"] = "S"
            for ifname in i[len(i) - 1].split():
                iface["members"] += [self.extract_iface(ifname)]
            r += [iface]
        return r
