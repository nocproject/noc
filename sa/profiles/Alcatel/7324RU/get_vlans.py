# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.7324RU.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "Alcatel.7324RU.get_vlans"
    implements = [IGetVlans]
    rx_vlan = re.compile(
        r"\s*(?P<vid>\d+)"
        r"\s*(?P<vname>[A-Za-z0-9\-\.]+)\n"
        r"([ 0-9]+)\n[ ]+(?P<vstatus>enabled|disabled)[ 0-9]+\n"
        r"([ \-xnf]+)\n[ ]+(?P<portmask>[\-tu]+)\s*"
        r"(?P<uplinkmask>[\-tu]*)", re.MULTILINE | re.IGNORECASE)

    def execute(self):
        v = self.cli("switch vlan show *")
        r = []
        for match in re.finditer(self.rx_vlan, v):
            if match.group("vstatus") == "enabled":
                r += [{
                    "vlan_id": int(match.group("vid")),
                    "name": match.group("vname")
                }]
        return r
