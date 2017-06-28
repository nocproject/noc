# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.7302.get_chassis_id
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
    name = "Alcatel.7302.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_id = re.compile(
        r"\s+base-bdg-addr\s*:\s*(?P<basemac>\S+)\s*\n"
        r"^\s+sys-mac-addr\s*:\s*(?P<sysmac>\S+)", re.MULTILINE)

    def execute(self):
        r = []
        v = self.cli("show system shub entry misc")
        match = self.rx_id.search(v)
        basemac = match.group("basemac")
        sysmac = match.group("sysmac")
        r += [{
            "first_chassis_mac": basemac,
            "last_chassis_mac": basemac
        }]
        if basemac != sysmac:
            r += [{
                "first_chassis_mac": sysmac,
                "last_chassis_mac": sysmac
            }]

        return r
