# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_chassis_id
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
    name = "Juniper.JUNOSe.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_slot = re.compile(
        r"^(?P<slot>\d+/\d+).+\d{10}\s+\d{10}\s+\S{3}\s+(?P<count>\d+)\s*\n", re.MULTILINE
    )
    rx_mac = re.compile(
        r"^(?P<slot>\d+/\d+)\s+(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})\s+\S+\s*\n",
        re.MULTILINE,
    )

    def execute(self):
        macs = []
        slots = []
        v = self.cli("show hardware | begin Adapters")
        for match in self.rx_slot.finditer(v):
            slots += [match.groupdict()]
        for match in self.rx_mac.finditer(v):
            slot = match.group("slot")
            for s in slots:
                if s["slot"] == slot:
                    base = match.group("mac")
                    macs += [
                        {
                            "first_chassis_mac": base,
                            "last_chassis_mac": MAC(base).shift(int(s["count"]) - 1),
                        }
                    ]
                    break
        return macs
