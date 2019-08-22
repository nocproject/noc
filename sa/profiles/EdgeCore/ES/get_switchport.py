# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# EdgeCore.ES.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport


class Script(BaseScript):
    """
    EdgeCore.ES.get_switchport
    @todo: ES4626 support
    @todo: QinQ
    """

    name = "EdgeCore.ES.get_switchport"
    interface = IGetSwitchport
    cache = True

    rx_interface_3526 = re.compile(
        r"Information of (?P<interface>[^\n]+?)\n", re.MULTILINE | re.IGNORECASE | re.DOTALL
    )
    rx_interface_swport_3526 = re.compile(
        r"Information of (?P<interface>[^\n]+?)\n"
        r".*?VLAN Membership Mode(|\s+):\s+(?P<mode>[^\n]+?)\n"
        r"(.*?Native VLAN(|\s+):\s+(?P<native>\d+))?"
        r".*?Allowed VLAN(|\s+):\s+(?P<vlans>.*?)"
        r"Forbidden VLAN(|\s+):",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )
    rx_interface_qinq_3526 = re.compile(
        r"802.1Q-tunnel Status(|\s+):\s+(?P<qstatus>\S+).*?802.1Q-tunnel Mode(|\s+):\s+(?P<qmode>\S+)",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )
    rx_interface_swport_4626 = re.compile(
        r"(?P<interface>[^\n]+)\n.*?Mode\s+:(?P<mode>\S+).*?Port VID\s+:(?P<pvid>\d+).*?",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )
    rx_member = re.compile(r"Member port of trunk \d+")
    rx_not_present = re.compile(r"Not present\.")
    rx_vlans = re.compile(r"\)([^,]+?)(\d)")
    rx_vlan_tag = re.compile(r"(?P<vlan>\d+)\((?P<tag>u|t)\)")
    rx_agg_member = re.compile(r"Type :Aggregation member")
    rx_trunk = re.compile(r"Trunk allowed Vlan: (?P<tagged>[^\n]+?)(\n|$)")

    def execute(self):
        r = []
        # Get portchannels
        portchannel_members = {}  # member -> (portchannel, type)
        for s in self.scripts.get_portchannel():
            portchannel_members[s["interface"]] = s["members"]
        interface_status = {}  # Interface -> status
        # Get interfaces status
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]
        if self.is_platform_3510 or self.is_platform_4612 or self.is_platform_ecs4100:
            cmd = self.cli("show interface switchport")
            for block in cmd.rstrip("\n\n").split("\n\n"):
                matchint = self.rx_interface_3526.search(block)
                if not matchint:
                    continue
                name = matchint.group("interface")
                swport = {
                    "interface": name,
                    "members": portchannel_members.get(name, ""),
                    "802.1ad Tunnel": False,
                    "802.1Q Enabled": False,
                    "tagged": "",
                    "status": interface_status.get(name, False),
                }
                if self.rx_member.search(block):
                    # skip portchannel members
                    r += [swport]
                    continue
                if self.rx_not_present.search(block):
                    # skip strange port state
                    r += [swport]
                    continue
                match = self.rx_interface_swport_3526.search(block)
                if match and match.group("mode").lower() in ["hybrid", "trunk"]:
                    swport["802.1Q Enabled"] = "True"
                # QinQ
                mqinq = self.rx_interface_qinq_3526.search(block)
                if mqinq and mqinq.group("qstatus").lower() == "enable":
                    if mqinq.group("qmode").lower() in ["access"]:
                        swport["802.1ad Tunnel"] = True
                    # untagged/tagged
                vlans = self.rx_vlans.sub(r"),\g<2>", match.group("vlans").rstrip(",\n "))
                vlans = vlans.replace(" ", "")
                untagged = None
                tagged = []
                for i in vlans.split(","):
                    m = self.rx_vlan_tag.search(i)
                    if m.group("tag") == "u":
                        if m.group("vlan") == match.group("native"):
                            untagged = m.group("vlan")
                    else:
                        tagged += [m.group("vlan")]
                if untagged:
                    swport["untagged"] = untagged
                swport["tagged"] = tagged
                r += [swport]
        elif self.is_platform_4626:
            cmd = self.cli("show interface switchport")
            for block in cmd.split("\n\n"):
                match = self.rx_interface_swport_4626.search(block)
                name = match.group("interface")
                swport = {
                    "interface": name,
                    "members": portchannel_members.get(name, ""),
                    "802.1ad Tunnel": False,
                    "802.1Q Enabled": False,
                    "tagged": "",
                    "status": interface_status.get(name, False),
                }
                if self.rx_agg_member.search(block):
                    # skip portchannel members
                    r += [swport]
                    continue
                if match.group("mode").lower() == "trunk":
                    swport["802.1Q Enabled"] = "True"
                swport["untagged"] = match.group("pvid")
                tagged = []
                p = self.rx_trunk.search(block)
                if p:
                    swport["tagged"] = self.expand_rangelist(p.group("tagged").replace(";", ","))
                r += [swport]
        else:
            raise self.NotSupportedError()
        return r
