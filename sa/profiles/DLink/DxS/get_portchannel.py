# ---------------------------------------------------------------------
# DLink.DxS.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "DLink.DxS.get_portchannel"
    interface = IGetPortchannel
    rx_trunk = re.compile(
        r"Group ID\s+:\s+(?P<trunk>\d+).+?Type\s+:\s+(?P<type>\S+).+?Member Port\s+:\s+(?P<members>\S+).+?Status\s+:\s+(?P<status>\S+)",
        re.MULTILINE | re.DOTALL,
    )

    def execute_cli(self):
        try:
            t = self.cli("show link_aggregation")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        for match in self.rx_trunk.finditer(t):
            r += [
                {
                    "interface": "T%s" % match.group("trunk"),
                    "members": self.expand_interface_range(match.group("members")),
                    "type": "L" if match.group("type").lower() == "lacp" else "S",
                }
            ]
        return r
