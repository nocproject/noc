# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Arista.EOS.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import re
## Python modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "Arista.EOS.get_switchport"
    implements = [IGetSwitchport]

    rx_line = re.compile(
        r"^(?P<port>\S\S\d+)\s+"
        r"(?P<untagged>\d+|None)\s+"
        r"(?P<tagged>.+)$"
    )

    def execute(self):
        r = []
        port_channel_members = {}  # portchannel -> [interfaces]
        interface_status = {}      # Interface -> stauts
        # Get interafces status
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]
        # Get portchannel members
        for s in self.scripts.get_portchannel():
            port_channel_members[s["interface"]] = s["members"]
        # Get switchport data
        v = self.cli("show interfaces vlans")
        for l in v.splitlines():
            match = self.rx_line.match(l)
            if match:
                name = self.profile.convert_interface_name(match.group("port"))
                p = {
                    "interface": name,
                    "members": port_channel_members.get(name, []),
                    "status": interface_status.get(name, False)
                }
                untagged = match.group("untagged")
                if untagged != "None":
                    p["untagged"] = int(untagged)
                tagged = match.group("tagged")
                if tagged != "-":
                    p["tagged"] = self.expand_rangelist(tagged)
                r += [p]
        return r
