# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport
from noc.lib.validators import is_int


class Script(BaseScript):
    name = "Huawei.VRP.get_switchport"
    interface = IGetSwitchport

    rx_vlan_comment = re.compile(r"\([^)]+\)", re.MULTILINE | re.DOTALL)
    rx_iftype = re.compile(r"^(\S+?)\d+.*$")

    def execute(self):
        rx_line = re.compile(
            r"(?P<interface>\S+)\s+(?P<mode>access|trunk|hybrid|trunking)\s+(?P<pvid>\d+)\s+(?P<vlans>(?:\d|\-|\s|\n)+)", re.MULTILINE)
        rx_descr = re.compile(
            r"^(?P<interface>\S+)\s+(?P<description>.+)", re.MULTILINE)

        # Get descriptions
        descriptions = {}
        try:
            c = self.cli("display interface description")
        except self.CLISyntaxError:
            rx_descr = re.compile(
                r"^(?P<interface>(?:Eth|GE|TENGE)\d+/\d+/\d+)\s+"
                r"(?P<status>(?:UP|(?:ADM\s)?DOWN))\s+(?P<speed>.+?)\s+"
                r"(?P<duplex>.+?)\s+"
                r"(?P<mode>access|trunk|hybrid|trunking|A|T|H)\s+"
                r"(?P<pvid>\d+)\s*(?P<description>.*)$", re.MULTILINE)
            try:
                c = self.cli("display brief interface")
            except self.CLISyntaxError:
                c = self.cli("display interface brief")

        for match in rx_descr.finditer(c):
            interface = self.profile.convert_interface_name(match.group("interface"))
            description = match.group("description").strip()
            if description.upper().startswith("HUAWEI"):
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
        known_vlans = set(
            [vlan["vlan_id"] for vlan in self.scripts.get_vlans()]
        )

        r = []
        for iface in descriptions:
            match = self.rx_iftype.match(iface)
            iftype = self.profile.if_types[match.group(1)]
            if iftype is None or iftype != "physical":
                continue  # Skip ignored interfaces

            members = []
            if iface.startswith("Eth-Trunk"):
                for p in portchannels:
                    if p["interface"] == iface:
                        members = p["members"]
            port = {
                "interface": iface,
                "status": interface_status.get(iface, False),
                "802.1Q Enabled": False,
                "802.1ad Tunnel": False,
                "members": members,
                "tagged": []
            }
            description = descriptions.get(iface)
            if description:
                port["description"] = description
            r += [port]

        # Get ports in vlans
        version = self.profile.fix_version(self.scripts.get_version())
        if version.startswith("5.3"):
            c = self.cli("display port allow-vlan")
        elif version.startswith("3.10"):
            rx_line = re.compile(
                r"""
                (?P<interface>\S+)\scurrent\sstate
                .*?
                PVID:\s(?P<pvid>\d+)
                .*?
                Port\slink-type:\s(?P<mode>access|trunk|hybrid|trunking)
                .*?
                (?:Tagged\s+VLAN\sID|VLAN\spermitted)?:\s(?P<vlans>.*?)\n
                """,
                re.MULTILINE | re.DOTALL | re.VERBOSE)
            c = self.cli("display interface", cached=True)
        else:
            try:
                c = self.cli("display port vlan")
            except self.CLISyntaxError:
                c = "%s\n%s" % (
                    self.cli("display port trunk"),
                    self.cli("display port hybrid")
                )

        for match in rx_line.finditer(c):
            for port in r:
                if port["interface"] == match.group("interface"):
                    tagged = []
                    trunk = match.group("mode") in ("trunk", "hybrid", "trunking")
                    if trunk:
                        vlans = match.group("vlans").strip()
                        if (
                            vlans and (vlans not in ["-", "none"]) and
                            is_int(vlans[0])
                        ):
                            vlans = self.rx_vlan_comment.sub("", vlans)
                            vlans = vlans.replace(" ", ",")
                            tagged = self.expand_rangelist(vlans)
                            # For VRP version 5.3
                            if r and r[-1]["interface"] == match.group("interface"):
                                r[-1]["tagged"] += [v for v in tagged if v in known_vlans]
                                continue
                        port["tagged"] = [v for v in tagged if v in known_vlans]
                        port["802.1Q Enabled"] = True

                    pvid = int(match.group("pvid"))
                    if pvid != 0 and match.group("mode") in ("access", "hybrid"):
                        port["untagged"] = pvid

        return r
