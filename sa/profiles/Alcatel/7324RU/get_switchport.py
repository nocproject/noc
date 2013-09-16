# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.7324RU.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport
from noc.lib.text import *
from collections import defaultdict

class Script(NOCScript):
    name = "Alcatel.7324RU.get_switchport"
    implements = [IGetSwitchport]
    rx_vlan = re.compile(
        r"[ ]*(?P<vid>\d+)[ ]*(?P<vname>[A-Za-z0-9\-\.]+)\n"
        r"([ 0-9]+)\n[ ]+(?P<vstatus>enabled|disabled)[ 0-9]+\n"
        r"([ \-xnf]+)\n[ ]+(?P<portmask>[\-tu]+)"
        r"[ ]*(?P<uplinkmask>[\-tu]*)",
        re.MULTILINE | re.IGNORECASE)

    def execute(self):
        tagged = defaultdict(list)
#        untagged = defaultdict(list)
        va = self.cli("adsl pvc show")
        vl = self.cli("switch vlan show *")
        r = []

        for line in parse_table(va):
            r += [{
                "interface": line[0],
                "untagged":  line[3],
                "tagged": [],
                "members": []
            }]
        for match in re.finditer(self.rx_vlan, vl):
            up = 0
            if match.group("vstatus") == "enabled":
                for i in match.group("uplinkmask"):
                    up += 1
                    if i == "T":
                        tagged[up] += [match.group("vid")]
#                    if i == "U":
#                        untagged[up]+=[match.group("vid")]
        for i in range(up):
            r += [{
                "interface": "enet"+str(i+1),
                "802.1Q Enabled": True,
#                "untagged": untagged[i+1],
                "tagged": tagged[i+1],
                "members": []
            }]
        return r