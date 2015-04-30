# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_oam_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetOAMStatus


class Script(NOCScript):
    name = "EdgeCore.ES.get_oam_status"
    implements = [IGetOAMStatus]

    rx_line = re.compile(
        r"^(?P<interface>1/\d+)\s+(?P<mac>\S+)\s+(?P<oui>\S+)\s+"
        r"(?P<caps_R>Disabled|Enabled)\s+(?P<caps_U>Disabled|Enabled)\s+"
        r"(?P<caps_L>Disabled|Enabled)\s+(?P<caps_V>Disabled|Enabled)",
        re.MULTILINE)

    def execute(self, **kwargs):
        r = []
        try:
            v = self.cli("show efm oam status remote interface ")
        except self.CLISyntaxError:
            raise self.NotSupportedError
        for match in self.rx_line.finditer(v):
            mac = match.group("mac")
            if mac == "00-00-00-00-00-00":
                continue
            iface = match.group("interface")
            # XXX: Tested only on ECS4210-12T platform
            iface = "Eth " + iface
            caps = []
            if match.group("caps_R") == "Enabled":
                caps += ["R"]
            if match.group("caps_U") == "Enabled":
                caps += ["U"]
            if match.group("caps_L") == "Enabled":
                caps += ["L"]
            if match.group("caps_V") == "Enabled":
                caps += ["V"]
            r += [{
                "interface": iface,
                "remote_mac": mac,
                "caps": caps
            }]
        return r
