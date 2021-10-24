# ---------------------------------------------------------------------
# Iskratel.ESCOM.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_portchannel import Script as BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Iskratel.ESCOM.get_portchannel"
    interface = IGetPortchannel
    cache = True

    def execute_cli(self):
        if not self.is_escom_l:
            self.logger.info("ESCOM L only supported Aggregator Group")
            return []
        r = []
        try:
            v = self.cli("show aggregator-group summary", cached=True)
        except self.CLISyntaxError:
            return []
        for group, po, ports in parse_table(v):
            r += [
                {
                    "interface": po.split("(")[0].strip(),
                    "members": [ll.split("(", 1)[0].strip() for ll in ports.split(",")],
                    "type": "L",
                }
            ]
        return r
