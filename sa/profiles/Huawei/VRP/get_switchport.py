# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport
import re


class Script(NOCScript):
    name = "Huawei.VRP.get_switchport"
    implements = [IGetSwitchport]
    rx_line = re.compile(
        r"^(?P<interface>\S+)\s+(?P<mode>access|trunk|hybrid)\s+(?P<pvid>\d+)\s+(?P<vlans>.+)", re.MULTILINE)
    rx_descr = re.compile(
        r"^(?P<interface>\S+)\s+(?P<description>.+)", re.MULTILINE)

    def execute(self):

        # Get descriptions
        descriptions = {}
        v = self.cli("display interface description")
        for match in self.rx_descr.finditer(v):
            interface = match.group("interface")
            description = match.group("description").strip()
            if description.startswith("HUAWEI"):
                description = ""
            if match.group("interface") != "Interface":
                descriptions[interface] = description

        # Get interafces status
        interface_status = {}
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]

        # Get portchannel
        portchannels = self.scripts.get_portchannel()

        # Get ports in vlans
        r = []
        for match in self.rx_line.finditer(self.cli("display port vlan")):
            port = {}
            tagged = []
            trunk = match.group("mode") in ("trunk", "hybrid")
            if trunk:
                vlans = match.group("vlans").strip()
                if vlans != "-":
                    vlans = vlans.replace(" ", ",")
                    tagged = self.expand_rangelist(vlans)
            members = []

            interface = match.group("interface")
            if interface.startswith("Eth-Trunk"):
                ifname = self.profile.convert_interface_name(interface)
                for p in portchannels:
                    if p["interface"] in {ifname, interface}:
                        members = p["members"]

            pvid = int(match.group("pvid"))
            # This is an exclusive Chinese networks ?
            if pvid == 0:
                pvid = 1

            port = {
                "interface": interface,
                "status": interface_status.get(interface, False),
                "802.1Q Enabled": trunk,
                "802.1ad Tunnel": False,
                "tagged": tagged,
                "members": members
            }
            if match.group("mode") in ("access", "hybrid"):
                port.update({"untagged": pvid})
            description = descriptions.get(interface, False)
            if description != "":
                port.update({"description": description})

            r += [port]
        return r
