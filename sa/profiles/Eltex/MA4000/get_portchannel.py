# ---------------------------------------------------------------------
# Eltex.MA4000.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "Eltex.MA4000.get_portchannel"
    interface = IGetPortchannel

    rx_cg = re.compile(
        r"^Channel group \d+\s*\n^\s*Mode: (?P<mode>\S+)\s*\n^(?P<members>.+)\s*\n",
        re.MULTILINE | re.DOTALL,
    )
    rx_iface = re.compile(r"^\s*Port\s*(?P<ifname>.+):", re.MULTILINE)

    def execute(self):
        r = []
        for cg in range(1, 9):
            c = self.cli("show channel-group summary %s" % cg)
            match = self.rx_cg.search(c)
            if match:
                r += [
                    {
                        "interface": "port-channel %s" % cg,
                        "type": "L" if match.group("mode") == "LACP" else "S",
                        "members": self.rx_iface.findall(match.group("members")),
                    }
                ]
        return r
