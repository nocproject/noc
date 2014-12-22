# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport
import re


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.get_switchport"
    implements = [IGetSwitchport]
    rx_line = re.compile(
        r"^(?P<interface>\S*\s*\d+(\/\d+)?)\s+(?P<status>\S+)\s+"
        r"(?P<mode>ACCESS|TRUNK)\s+(?P<access_vlan>\d+)\s+"
        r"(?P<untagged>\d+)\s+\S+\s+(?P<vlans>\d+\S+)?\n", re.MULTILINE)

    def execute(self):
        r = []
        c = self.cli("show interfaces switchport")
        for match in self.rx_line.finditer(c):
            trunk = match.group("mode") == "TRUNK"
            pvid = None
            if trunk:
                pvid = int(match.group("untagged"))
                vlans = match.group("vlans")
                if vlans is not None and vlans != '':
                    if vlans == "ALL":
                        tagged = range(1, 4095)
                    else:
                        tagged = self.expand_rangelist(vlans)
                else:
                    tagged = []
            else:
                pvid = int(match.group("access_vlan"))
                tagged = []
            members = []
            interface = match.group("interface")
            if interface.startswith("AggregatePort"):
                shortname = self.profile.convert_interface_name(interface)
                for p in self.scripts.get_portchannel():
                    if p["interface"] == shortname:
                        members = p["members"]
            r += [{
                "interface": interface,
                "status": match.group("status") == "enabled",
                #"description"    : "Dummy";
                "802.1Q Enabled": trunk,
                "802.1ad Tunnel": False,
                "untagged": pvid,
                "tagged": tagged,
                "members": members
                }]
        return r
