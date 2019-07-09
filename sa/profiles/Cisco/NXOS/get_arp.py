# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.NXOS.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "Cisco.NXOS.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<ip>([0-9]{1,3}\.){3}[0-9]{1,3})\s+\S+\s+(?P<mac>\S+)\s+(?P<interface>\S+)",
        re.MULTILINE,
    )

    def execute(self, vrf=None):
        if vrf:
            s = self.cli("show ip arp vrf %s | no-more" % vrf)
        else:
            try:
                s = self.cli("show ip arp all | no-more")
            except self.CLISyntaxError:
                s = self.cli("show ip arp vrf all | no-more")

        r = []
        for match in self.rx_line.finditer(s):
            mac = match.group("mac")
            if mac.lower() == "incomplete":
                r += [{"ip": match.group("ip"), "mac": None, "interface": None}]
            else:
                r += [match.groupdict()]
        return r
