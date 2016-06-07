# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Iskratel.MSAN.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "Iskratel.MSAN.get_portchannel"
    interface = IGetPortchannel

    rx_p = re.compile(
        r"^(?P<iface>\d+/\d+).+?Static\s+(?P<port1>\d+/\d+).+?"
        r"(?P<port2>\d+/\d+)", re.MULTILINE | re.DOTALL)

    def execute(self):
        match = self.rx_p.search(self.cli("show port-channel all"))
        if match:
            return [{
                "interface": match.group("iface"),
                "members": [match.group("port1"), match.group("port2")],
                "type": "S"
            }]
        else:
            return []
