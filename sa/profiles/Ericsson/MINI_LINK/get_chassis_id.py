# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ericsson.MINI_LINK.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Ericsson.MINI_LINK.get_chassis_id"
    interface = IGetChassisID

    rx_mac_begin = re.compile(
        r"Primary/First MAC Address:\s+(?P<mac>\S+)")
    rx_mac_end = re.compile(
        r"Last MAC Address:\s+(?P<mac>\S+)")

    def execute(self):
        r = []
        for i in [0, 1, 2, 3]:  # XXX: need more examples
            c = self.cli_clean("show board 1/%s" % i)
            if "No board in slot" in c:
                continue
            match1 = self.re_search(self.rx_mac_begin, c)
            match2 = self.re_search(self.rx_mac_end, c)
            r += [{
                "first_chassis_mac": match1.group("mac"),
                "last_chassis_mac": match2.group("mac")
            }]
        return r
