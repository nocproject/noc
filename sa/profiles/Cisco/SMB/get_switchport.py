# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.SMB.get_switchport
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport


class Script(BaseScript):
    name = "Cisco.SMB.get_switchport"
    cache = True
    interface = IGetSwitchport

    rx_body = re.compile(
        r"^Port : .+"
        r"Port Mode: (?P<amode>\S+).+"
        r".+NATIVE[^\d]+(?P<nvlan>\d+).+",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_portmembers = re.compile(
        r"^\s*(?P<vid>\d+)\s+\S+\s+(?P<erule>\S+)\s+(?P<mtype>\S+)")
    rx_descr_if = re.compile(r"^(?P<interface>\S+)\s*(?P<description>\S+)?")

    def get_description(self):
        r = []
        s = self.cli("show interfaces description", cached=True)
        for ll in s.split("\n"):
            match = self.rx_descr_if.match(ll.strip())
            if not match:
                continue
            else:
                interface = match.group("interface")
                if interface in ("Port", "Ch", "-------"):
                    continue
            r += [{
                "interface": self.profile.convert_interface_name(interface),
                "description": match.group("description")
            }]
        return r

    def execute(self):
        # Get portchannel members
        portchannels = {}  # portchannel name -> [members]
        for p in self.scripts.get_portchannel():
            portchannels[p["interface"]] = p["members"]

        # Get descriptions
        descriptions = {}  # interface name -> description
        interfaces = {}   # interface name -> status (True - up, False - down)
        # Prepare interface statuses
        for p in self.get_description():
            descriptions[p["interface"]] = p["description"]
            interfaces[p["interface"]] = False  # default is down
        for po in portchannels.keys():
            interfaces[po] = False
        if not interfaces:
            return []

        # Get vlans, as set([1,2,3,10])
        known_vlans = set([vlan["vlan_id"] for vlan in self.scripts.get_vlans()])

        # Set up interface statuses
        for intstatus in self.scripts.get_interface_status():
            if intstatus['interface'] in interfaces.keys():
                interfaces[intstatus['interface']] = intstatus['status']

        r = []  # reply
        # For each interface
        for interface in interfaces.keys():
            v = self.cli("show interfaces switchport %s" % interface)
            is_trunk = None
            is_qnq = None
            untagged = None
            tagged = []

            # Parse header
            match = self.rx_body.search(v)
            amode = match.group("amode").strip().lower()
            # can native vlan mismatch with untagged?
            untagged = int(match.group("nvlan"))
            if amode in ("trunk", "general"):
                is_trunk = True
                is_qnq = False
            elif amode in ("access"):
                is_trunk = False
                is_qnq = False
            elif amode in ("customer"):
                is_qnq = True
                is_trunk = True

            # Parse list of vlans
            for ll in v.split("\n"):
                match = self.rx_portmembers.match(ll.strip())
                if match:
                    vid = int(match.group("vid"))
                    erule = match.group("erule").lower()
                    if erule in ("tagged"):
                        tagged.append(vid)

            iface = {
                "interface": interface,
                "status": interfaces[interface],
                "tagged": [vl for vl in tagged if vl in known_vlans],
                "members": portchannels.get(interface, []),
                "802.1Q Enabled": is_trunk,
                "802.1ad Tunnel": is_qnq,
            }
            if untagged:
                iface["untagged"] = untagged
            if interface in descriptions.keys():
                if descriptions[interface]:
                    iface["description"] = descriptions[interface]

            r += [iface]
        return r
