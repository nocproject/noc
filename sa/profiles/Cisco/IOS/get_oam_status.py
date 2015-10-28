# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_oam_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetOAMStatus


class Script(BaseScript):
    name = "Cisco.IOS.get_oam_status"
    interface = IGetOAMStatus

    rx_line = re.compile(
        r"^\s*(?P<interface>\S+)\s+"
        r"(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})\s+"
        r"\S+\s+"
        r"\S+\s+"
        r"(?P<caps>\S+)\s*$"
    )

    def execute(self, **kwargs):
        r = []
        try:
            v = self.cli("show ethernet oam summary")
        except self.CLISyntaxError:
            raise self.NotSupportedError
        for l in v.splitlines():
            match = self.rx_line.match(l)
            if match:
                iface = match.group("interface").strip()
                mac = match.group("mac")
                if mac == "-":
                    continue
                caps = []
                ic = match.group("caps")
                if "L" in ic:
                    caps += ["L"]
                r += [{
                    "interface": iface,
                    "remote_mac": mac,
                    "caps": caps
                }]
        return r
