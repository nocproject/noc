# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.WLC.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Cisco.WLC.get_chassis_id"
    cache = True
    interface = IGetChassisID

    ##
    ## Cisco WLC 5508
    ##
    rx_wlc5508 = re.compile(
        r"^Burned-in MAC Address\.*\s(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    @BaseScript.match(platform__regex=r"AIR-CT5508.*")
    def execute_wlc5508(self):
        v = self.cli("show sysinfo")
        match = self.re_search(self.rx_wlc5508, v)
        base = match.group("id")
        return [{
            "first_chassis_mac": base,
            "last_chassis_mac": base
        }]


    ##
    ## Other
    ##
    @BaseScript.match()
    def execute_not_supported(self):
        raise self.NotSupportedError()
