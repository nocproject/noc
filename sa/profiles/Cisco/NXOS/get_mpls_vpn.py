# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.NXOS.get_mpls_vpn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmplsvpn import IGetMPLSVPN


class Script(BaseScript):
    name = "Cisco.NXOS.get_mpls_vpn"
    interface = IGetMPLSVPN

    rx_line_split = re.compile(r"^VRF-Name:\s+", re.MULTILINE)
    rx_line_name = re.compile(r"^(?P<name>\S+),\s+VRF-ID:\s(?P<id>\d+),\s+State:\s+(?P<state>Up|Down)\s+",
                              re.MULTILINE)
    rx_line_rd = re.compile(r"^\s+RD:\s(?P<rd>\d:\d)\s*", re.MULTILINE)

    portchannel_members = {}

    def _get_portchannel_members(self, iface):
        iface = self.profile.convert_interface_name(iface)
        if not self.portchannel_members:
            for pc in self.scripts.get_portchannel():
                i = pc["interface"]
                self.portchannel_members[i] = pc["members"]
        if iface in self.portchannel_members:
            return self.portchannel_members[iface]
        else:
            return []

    def execute(self, **kwargs):
        t = self.cli("show vrf interface")
        vrfif = {}
        firstline = True
        for l in t.splitlines():
            if firstline:
                firstline = False
                continue
            l = l.strip().split()
            if l[1] not in vrfif.keys():
                vrfif[l[1]] = []
            vrfif[l[1]].append(l[0])
        vpns = []

        v = self.cli("show vrf detail")
        for I in self.rx_line_split.split(v)[1:]:
            match = self.re_search(self.rx_line_name, I)
            name = match.group("name")
            match = self.re_search(self.rx_line_rd, I)
            rd = match.group("rd")

            vpn = {
                "type": "VRF",
                "status": True,
                "name": name,
                "interfaces": vrfif.get(name, []),
                "rd": vrfif.get(rd, "0:0")
            }
            vpns += [vpn]

        return vpns
