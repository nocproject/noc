# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
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
    name = "Cisco.IOS.get_switchport"
    cache = True
    interface = IGetSwitchport

    rx_cont = re.compile(r",\s*$\s+", re.MULTILINE)
    rx_line = re.compile(r"\n+Name:\s+", re.MULTILINE)
    rx_body = re.compile(r"^(?P<interface>\S+).+"
                         "^Administrative Mode: (?P<amode>.+).+"
                         "^Operational Mode: (?P<omode>.+).+"
                         "^Administrative Trunking Encapsulation:.+"
                         "^Access Mode VLAN: (?P<avlan>\d+) \(.+\).+"
                         "^Trunking Native Mode VLAN: (?P<nvlan>\d+) \(.+\).+"
                         "^Trunking VLANs Enabled: (?P<vlans>.+?)$",
                         #"Pruning VLANs Enabled:",
                         re.MULTILINE | re.DOTALL)

    rx_descr_if = re.compile(
        r"^(?P<interface>\S+)\s+(?:up|down|admin down|deleted)\s+"
        r"(?:up|down)\s+(?P<description>.+)")
    rx_tagged = re.compile(
        r"^Port\s+Vlans allowed on trunk\s*\n"
        r"^\S+\s+([0-9\-\,]+)\s*\n", re.MULTILINE)

    rx_conf_iface = re.compile(
        r"^\s*interface (?P<ifname>\S+)\s*\n"
        r"(^\s*description (?P<descr>.+?)\n)?"
        r"(^\s*switchport trunk native vlan (?P<untagged>\d+)\s*\n)?"
        r"^\s*switchport trunk encapsulation dot1q\s*\n"
        r"^\s*switchport trunk allowed vlan (?P<vlans>.+?)"
        r"^\s*switchport mode (?P<mode>trunk|access)",
        re.MULTILINE | re.DOTALL)

    def parse_config(self):
        r = []
        c = self.scripts.get_config()
        for match in self.rx_conf_iface.finditer(c):
            vlans = match.group("vlans").replace("switchport trunk allowed vlan add", ",")
            iface = {
                "interface": match.group("ifname"),
                "tagged": self.expand_rangelist(vlans),
                "members": [],
                "802.1Q Enabled": True,
                "802.1ad Tunnel": False,
            }
            if match.group("untagged"):
                iface["untagged"] = match.group("untagged")
            if match.group("descr"):
                iface["description"] = match.group("descr")
            r += [iface]
        return r


    def get_description(self):
        r = []
        s = self.cli("show interfaces description", cached=True)
        for l in s.split("\n"):
            match = self.rx_descr_if.match(l.strip())
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
            v = self.cli("show interfaces switchport")
        except self.CLISyntaxError:
            # Cisco Catalist 3500 XL do not have this command
            #raise self.NotSupportedError()
            return self.parse_config()
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
                continue  #raise self.NotSupportedError()

            interface = self.profile.convert_interface_name(
                match.group("interface"))
            is_trunk = match.group("amode").strip() == "trunk"

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
                    try:
                        c = self.cli("show interface %s trunk" % interface)
                        match1 = self.rx_tagged.search(c)
                        if match1:  # If not `none` in returned list
                            tagged = self.expand_rangelist(match1.group(1))
                    except self.CLISyntaxError:
                        # Return anything
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
                "tagged": [v for v in tagged if v in known_vlans],
                "members": portchannels.get(interface, []),
                "802.1Q Enabled": is_trunk,
                "802.1ad Tunnel": False,
            }
            if untagged:
                iface["untagged"] = untagged
            if interface in descriptions:
                iface["description"] = descriptions[interface]

            r += [iface]
        return r
