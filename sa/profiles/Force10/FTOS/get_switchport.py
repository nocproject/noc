# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetSwitchport
import re

rx_portchannel_member = re.compile(r"^(\S+\s+\S+)\s+\((Port-channel\s+\d+)\)")


class Script(noc.sa.script.Script):
    name = "Force10.FTOS.get_switchport"
    implements = [IGetSwitchport]

    def execute(self):
        r = []
        port_channel_members = {}  # portchannel -> [interfaces]
        interface_status = {}      # Interface -> stauts
        # Get interafces status
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]
        # Get switchport data
        for s in self.cli("show interface switchport").split("\n\nName: ")[1:]:
            if not s:
                continue
            l = s.splitlines()
            # Check interface is portchannel member
            name = l.pop(0).strip()
            match = rx_portchannel_member.match(name)
            if match:
                # Skip portchannel members
                name, pc = match.groups()
                pc = self.profile.convert_interface_name(pc)
                name = self.profile.convert_interface_name(name)
                try:
                    port_channel_members[pc] += [name]
                except KeyError:
                    port_channel_members[pc] = [name]
                continue
            # Parse name, description and 802.1Q status
            name = self.profile.convert_interface_name(name)
            p = {
                "interface": name,
                "members": port_channel_members.get(name, []),
                "802.1ad Tunnel": False,
                "tagged": "",
                "status": interface_status.get(name, False)
            }
            vlan_membership_found = False
            while l:
                ll = l.pop(0)
                if ll.startswith("Description: "):
                    p["description"] = ll[12:].strip()
                elif ll.startswith("802.1QTagged:"):
                    p["802.1Q Enabled"] = "True" in ll
                elif ll == "Vlan membership:":
                    vlan_membership_found = True
                    break
            if not vlan_membership_found:
                continue
            # Parse vlans
            l.pop(0)
            for ll in l:
                if not ll:
                    continue
                # Untagged
                if ll.startswith("U"):
                    x, y = ll.split()
                    p["untagged"] = y
                elif ll.startswith("T"):
                    x, y = ll.split()
                    p["tagged"] = y
                elif ll.startswith(" "):
                    p["tagged"] += ll.strip()
            # Expand tagged
            p["tagged"] = self.expand_rangelist(p["tagged"])
            r += [p]
        return r
