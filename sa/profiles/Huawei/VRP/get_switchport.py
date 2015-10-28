# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport
import re


class Script(BaseScript):
    name = "Huawei.VRP.get_switchport"
    interface = IGetSwitchport
    rx_line = re.compile(
        r"(?P<interface>\S+)\s+(?P<mode>access|trunk|hybrid|trunking)\s+(?P<pvid>\d+)\s+(?P<vlans>(?:\d|\-|\s|\n)+)", re.MULTILINE)
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

        # Get vlans
        known_vlans = set([vlan["vlan_id"] for vlan in
                           self.scripts.get_vlans()])

        # Get ports in vlans
        r = []
        if self.match_version(version__startswith="5.3"):
            v = self.cli("display port allow-vlan")
        else:
            v = self.cli("display port vlan")

        for match in self.rx_line.finditer(v):
            port = {}
            tagged = []
            trunk = match.group("mode") in ("trunk", "hybrid", "trunking")
            if trunk:
                vlans = match.group("vlans").strip()
                if vlans != "-":
                    vlans = vlans.replace(" ", ",")
                    tagged = self.expand_rangelist(vlans)
                    # For VRP version 5.3
                    if r and r[-1]["interface"] == match.group("interface"): 
                        r[-1]["tagged"] += [v for v in tagged if v in known_vlans]
                        continue
            members = []

            interface = match.group("interface")
            if interface.startswith("Eth-Trunk"):
                ifname = self.profile.convert_interface_name(interface)
                for p in portchannels:
                    if p["interface"] in (ifname, interface):
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
                "tagged": [v for v in tagged if v in known_vlans],
                "members": members
            }
            if match.group("mode") in ("access", "hybrid"):
                port["untagged"] = pvid
            description = descriptions.get(interface)
            if description:
                port["description"] = description

            r += [port]
        return r
