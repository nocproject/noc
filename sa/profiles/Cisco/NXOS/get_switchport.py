# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.NXOS.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport


class Script(BaseScript):
    name = "Cisco.NXOS.get_switchport"
    cache = True
    interface = IGetSwitchport

    rx_cont = re.compile(r",\s*$\s+", re.MULTILINE)
    rx_line = re.compile(r"\n+Name:\s+", re.MULTILINE)
    rx_body = re.compile(r"^(?P<interface>\S+).+"
                         "^  Switchport: .+"
                         "^  Switchport Monitor: .+"
                         "^  Operational Mode: (?P<omode>\S+).+"
                         "^  Access Mode VLAN: (?P<avlan>\d+) \(.+\).+"
                         "^  Trunking Native Mode VLAN: (?P<nvlan>\d+) \(.+\).+"
                         "^  Trunking VLANs Allowed: (?P<vlans>.+?)$",
                         # "Pruning VLANs Enabled:",
                         re.MULTILINE | re.DOTALL)

    rx_body_name = re.compile(r"^(?P<interface>\S+).+", re.MULTILINE)

    rx_body_omode = re.compile(
        r"^Operational Mode: (?P<omode>\S+)\s*$", re.MULTILINE)

    rx_body_nvlan = re.compile(
        r"^Trunking Native Mode VLAN: (?P<nvlan>\d+) \(.+\).+", re.MULTILINE)

    rx_descr_if = re.compile(r"^(?P<interface>\S+)\s+(?:up|down|admin down|deleted)\s+(?:up|down)\s+"
                             r"(?P<description>.+)")

    def get_description(self):
        r = []
        s = self.cli("show interface description", cached=True)
        for ll in s.split("\n"):
            match = self.rx_descr_if.match(ll.strip())
            if not match:
                continue
            r += [{
                "interface": self.profile.convert_interface_name(match.group("interface")),
                "description": match.group("description")
            }]
        return r

    def execute(self):
        r = []
        try:
            v = self.cli("show interface switchport")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        v = "\n" + v
        v = self.rx_cont.sub(",", v)  # Unwind continuation lines
        # Get portchannel members
        portchannels = {}  # portchannel name -> [members]
        for p in self.scripts.get_portchannel():
            portchannels[p["interface"]] = p["members"]
        # Get descriptions
        descriptions = {}  # interface name -> description
        for p in self.get_description():
            descriptions[p["interface"]] = p["description"]
        # Get vlans
        known_vlans = set([vlan["vlan_id"] for vlan in
                           self.scripts.get_vlans()])
        # For each interface
        for s in self.rx_line.split(v)[1:]:
            match = self.rx_body.search(s)
            if not match:
                continue
                # raise self.NotSupportedError()

            interface = self.profile.convert_interface_name(
                match.group("interface"))
            is_trunk = match.group("omode").strip() == "trunk"

            if is_trunk:
                untagged = int(match.group("nvlan"))
                vlans = match.group("vlans").strip()
                if vlans == "ALL":
                    tagged = range(1, 4095)
                elif vlans.upper() == "NONE":
                    tagged = []
                #
                # Cisco hides info like this
                # 3460,3463-3467,3469-3507,3512,3514,3516-3519,3528,(more)
                #
                elif "more" in vlans:
                    tagged = self.expand_rangelist(vlans[:-7])
                else:
                    tagged = self.expand_rangelist(vlans)
                if untagged in tagged:
                    # Exclude native vlan from tagged
                    tagged.remove(untagged)
            else:
                untagged = int(match.group("avlan"))
                tagged = []

            iface = {
                "interface": interface,
                "status": match.group("omode").strip() != "down",
                "tagged": [vv for vv in tagged if vv in known_vlans],
                "members": portchannels.get(interface, []),
                "802.1Q Enabled": is_trunk,
                "802.1ad Tunnel": False
            }
            if untagged:
                iface["untagged"] = untagged
            if interface in descriptions:
                iface["description"] = descriptions[interface]

            r += [iface]
        return r
