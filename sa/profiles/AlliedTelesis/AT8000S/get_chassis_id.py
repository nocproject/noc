# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8000S.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.text import parse_table


class Script(BaseScript):
    name = "AlliedTelesis.AT8000S.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>\S+)", re.MULTILINE)

    def execute(self):
        match = self.rx_mac.search(self.cli("show system", cached=True))
        if match:
            return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}

        macs = []
        try:
            v = self.cli("show stack", cached=True)
            for i in parse_table(v, footer="Topology is "):
                for m in macs:
                    if m == i[1]:
                        break
                else:
                    macs += [i[1]]
        except self.CLISyntaxError:
            pass

        if macs:
            macs.sort()
            return [
                {"first_chassis_mac": f, "last_chassis_mac": t}
                for f, t in self.macs_to_ranges(macs)
            ]
