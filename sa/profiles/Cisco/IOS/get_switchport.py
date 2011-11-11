# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "Cisco.IOS.get_switchport"
    cache = True
    implements = [IGetSwitchport]

    rx_line = re.compile(r"\n\nName:\s+", re.MULTILINE)
    rx_body = re.compile(r"^(?P<interface>\S+).+^Administrative Mode: (?P<amode>.+).+^Operational Mode: (?P<omode>.+).+^Administrative Trunking Encapsulation:.+^Access Mode VLAN: (?P<avlan>\d+) \(.+\).+Trunking Native Mode VLAN: (?P<nvlan>\d+) \(.+\).+Trunking VLANs Enabled: (?P<vlans>.+)Pruning VLANs Enabled:", re.MULTILINE | re.DOTALL)

    def execute(self):
        r = []
        try:
            v = self.cli("show interfaces switchport")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        v = "\n" + v

        # For each interface
        for s in self.rx_line.split(v)[1:]:
            match = self.rx_body.search(s)
            if not match:
                raise self.NotSupportedError()

            interface = match.group("interface")
            trunk = match.group("amode").strip() == "trunk"

            if trunk:
                untagged = match.group("nvlan")
                vlans = match.group("vlans").strip()
                if vlans == "ALL":
                    tagged = range(1, 4095)
                else:
                    tagged = self.expand_rangelist(vlans)
            else:
                untagged = match.group("avlan")
                tagged = []

            members = []
            if interface.startswith("Po"):
                shortname = self.profile.convert_interface_name(interface)
                for p in self.scripts.get_portchannel():
                    if p["interface"] == shortname:
                        members = p["members"]

            r += [{
                "interface"     : interface,
                "status"        : match.group("omode").strip() != "down",
                #"description"    : "Dummy";
                "tagged"        : tagged,
                "untagged"      : int(untagged),
                "members"       : members,
                "802.1Q Enabled": trunk,
                "802.1ad Tunnel": False,
            }]
        return r
