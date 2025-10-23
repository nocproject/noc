# ---------------------------------------------------------------------
# Iskratel.MSAN.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "Iskratel.MSAN.get_portchannel"
    interface = IGetPortchannel

    rx_p = re.compile(
        r"^(?P<iface>\d+/\d+).+?Static\s+(?P<port1>\d+/\d+).+?(?P<port2>\d+/\d+)",
        re.MULTILINE | re.DOTALL,
    )

    def execute_cli(self):
        r = []
        try:
            c = self.cli("show port-channel all")
        except self.CLISyntaxError:
            return []
        for match in self.rx_p.finditer(c):
            r += [
                {
                    "interface": match.group("iface"),
                    "members": [match.group("port1"), match.group("port2")],
                    "type": "S",
                }
            ]
        return r
