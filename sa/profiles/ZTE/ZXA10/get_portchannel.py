# ---------------------------------------------------------------------
# ZTE.ZXA10.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "ZTE.ZXA10.get_portchannel"
    interface = IGetPortchannel

    rx_num = re.compile(r"^(\d+)", re.MULTILINE)
    rx_iface = re.compile(
        r"^(x?gei[\_\-]\d+/\d+/\d+)(?:\[[SA\* ]+\])?\s+(?:active|inactive)",
        re.MULTILINE | re.IGNORECASE,
    )

    def execute_cli(self):
        r = []
        try:
            s = self.cli("show lacp internal")
        except self.CLISyntaxError:
            return []
        for i in s.split("Smartgroup:"):
            if not self.rx_num.search(i):
                continue
            iface = "smartgroup" + self.rx_num.search(i)[0]
            iface = {"interface": iface, "type": "L", "members": []}
            iface["members"] = self.rx_iface.findall(i)
            r += [iface]
        return r
