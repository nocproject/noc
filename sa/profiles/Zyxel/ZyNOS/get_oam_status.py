# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Zyxel.ZyNOS.get_oam_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetoamstatus import IGetOAMStatus


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_oam_status"
    interface = IGetOAMStatus
=======
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_oam_status
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
    name = "Zyxel.ZyNOS.get_oam_status"
    implements = [IGetOAMStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_line = re.compile(
        r"^(?P<interface>\S+)\s+\S+\s+(?P<mac>[0-9a-f:]+)\s+\S+\s+\S+\s*"
        r"(?P<caps>[RLU\s]*)$",
        re.MULTILINE
    )

    def execute(self, **kwargs):
        r = []
        try:
            cmd = self.cli("show ethernet oam summary")
        except self.CLISyntaxError:
            raise self.NotSupportedError
        for match in self.rx_line.finditer(cmd):
            iface = match.group("interface")
            mac = match.group("mac")
            caps = []
            ic = match.group("caps")
            if "L" in ic:
                caps += ["L"]
            if "R" in ic:
                caps += ["R"]
            if "U" in ic:
                caps += ["U"]
            r += [{
                "interface": iface,
                "remote_mac": mac,
                "caps": caps
            }]
        return r
