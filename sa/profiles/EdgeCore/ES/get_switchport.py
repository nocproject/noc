# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    """
    EdgeCore.ES.get_switchport
    @todo: ES4626 support
    @todo: QinQ
    """
    name = "EdgeCore.ES.get_switchport"
    implements = [IGetSwitchport]
    cache = True

    rx_interface_3526 = re.compile(r"Information of (?P<interface>[^\n]+?)\n",
                                   re.MULTILINE | re.IGNORECASE | re.DOTALL)
    rx_interface_swport_3526 = re.compile(
        r"Information of (?P<interface>[^\n]+?)\n.*?VLAN Membership Mode(|\s+):\s+(?P<mode>[^\n]+?)\n.*?Native VLAN(|\s+):\s+(?P<native>\d+).*?Allowed VLAN(|\s+):\s+(?P<vlans>.*?)Forbidden VLAN(|\s+):",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)
    rx_interface_qinq_3526 = re.compile(
        r"802.1Q-tunnel Status(|\s+):\s+(?P<qstatus>\S+).*?802.1Q-tunnel Mode(|\s+):\s+(?P<qmode>\S+)",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)
    rx_interface_swport_4626 = re.compile(
        r"(?P<interface>[^\n]+)\n.*?Mode\s+:(?P<mode>\S+).*?Port VID\s+:(?P<pvid>\d+).*?",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)

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

        if (self.match_version(platform__contains="3526") or
           self.match_version(platform__contains="3510") or
           self.match_version(platform__contains="2228N") or
           self.match_version(platform__contains="3528") or
           self.match_version(platform__contains="3552") or
           self.match_version(platform__contains="4612") or
           self.match_version(platform__contains="ECS4210")):
            cmd = self.cli("show interface switchport")
            for block in cmd.rstrip("\n\n").split("\n\n"):
                matchint = self.rx_interface_3526.search(block)
                name = matchint.group("interface")
                swport = {
                    "interface": name,
                    "members": portchannel_members.get(name, ""),
                    "802.1ad Tunnel": False,
                    "802.1Q Enabled": False,
                    "tagged": "",
                    "status": interface_status.get(name, False)
                }
                if re.search(r"Member port of trunk \d+", block):
                    # skip portchannel members
                    r += [swport]
                    continue
                match = self.rx_interface_swport_3526.search(block)
                if match.group("mode").lower() in ["hybrid", "trunk"]:
                    swport["802.1Q Enabled"] = "True"
                # QinQ
                mqinq = self.rx_interface_qinq_3526.search(block)
                if mqinq and mqinq.group("qstatus").lower() == "enable":
                    if mqinq.group("qmode").lower() in ["access"]:
                        swport["802.1ad Tunnel"] = True
                    # untagged/tagged
                p = re.compile("\)([^,]+?)(\d)")
                vlans = p.sub(r"),\g<2>", match.group("vlans").rstrip(",\n "))
                vlans = vlans.replace(" ", "")
                untagged = None
                tagged = []
                for i in vlans.split(","):
                    m = re.search("(?P<vlan>\d+)\((?P<tag>u|t)\)", i)
                    if m.group("tag") == "u":
                        if m.group("vlan") == match.group("native"):
                            untagged = m.group("vlan")
                    else:
                        tagged += [m.group("vlan")]
                if untagged:
                    swport["untagged"] = untagged
                swport["tagged"] = tagged
                r += [swport]
        elif self.match_version(platform__contains="4626"):
            cmd = self.cli("show interface switchport")
            for block in cmd.split("\n\n"):
                match = self.rx_interface_swport_4626.search(block)
                name = match.group("interface")
                swport = {"interface": name,
                          "members": portchannel_members.get(name, ""),
                          "802.1ad Tunnel": False,
                          "802.1Q Enabled": False,
                          "tagged": "",
                          "status": interface_status.get(name, False)}
                if re.search(r"Type :Aggregation member", block):
                # skip portchannel members
                    r += [swport]
                    continue
                if match.group("mode").lower() == "trunk":
                    swport["802.1Q Enabled"] = "True"
                swport["untagged"] = match.group("pvid")
                tagged = []
                p = re.search("Trunk allowed Vlan: (?P<tagged>[^\n]+?)(\n|$)",
                              block)
                if p:
                    swport["tagged"] = self.expand_rangelist(
                        p.group("tagged").replace(";", ","))
                r += [swport]
        else:
            raise self.NotSupportedError()
        return r
