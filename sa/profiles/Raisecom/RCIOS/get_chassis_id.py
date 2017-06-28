# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Raisecom.RCIOS.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Raisecom.RCIOS.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"mac-addr: (?P<mac>\S+)", re.MULTILINE)

    def execute(self):
        mac = ()
        v = self.cli("show version", cached=True)
        macs = self.rx_mac.findall(v)
        if macs:
            macs.sort()
            return [{
                "first_chassis_mac": f,
                "last_chassis_mac": t
            } for f, t in self.macs_to_ranges(macs)]
