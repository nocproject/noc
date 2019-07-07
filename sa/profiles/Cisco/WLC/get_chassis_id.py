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
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Cisco.WLC.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_wlc5508 = re.compile(r"^Burned-in MAC Address\.*\s(?P<id>\S+)", re.IGNORECASE | re.MULTILINE)

    def execute_wlc5508(self):
        """
        Cisco WLC 5508
        :return:
        """
        v = self.cli("show sysinfo")
        match = self.re_search(self.rx_wlc5508, v)
        base = match.group("id")
        return [{"first_chassis_mac": base, "last_chassis_mac": base}]

    def execute_cli(self):
        if self.is_platform_5508:
            return self.execute_wlc5508()
        raise self.NotSupportedError()
