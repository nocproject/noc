# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOSXR.get_oam_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetOAMStatus


class Script(NOCScript):
    name = "Cisco.IOSXR.get_oam_status"
    implements = [IGetOAMStatus]

    rx_line = re.compile(
        r"^\s*(?P<interface>\S+)\s+"
        r"(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})\s+"
        r"\S+\s+"
        r"\S+\s+"
        r"(?P<caps>\S+)\s*$",
        re.IGNORECASE
    )

    def execute(self, **kwargs):
        r = []
        try:
            v = self.cli("show ethernet oam discovery brief")
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
