# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.NXOS.get_mpls_vpn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
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
    rx_line_name = re.compile(
        r"^(?P<name>\S+),\s+VRF-ID:\s(?P<id>\d+),\s+"
        r"State:\s+(?P<state>Up|Down)\s+",
        re.MULTILINE
    )
    rx_line_rd = re.compile(r"^\s+RD:\s(?P<rd>\d\S*:\d)\s*", re.MULTILINE)

    def execute(self, **kwargs):
        t = self.cli("show vrf interface")
        vrfif = {}
        firstline = True
        for ll in t.splitlines():
            if firstline:
                firstline = False
                continue
            ll = ll.strip().split()
            if ll[1] not in vrfif.keys():
                vrfif[ll[1]] = []
            vrfif[ll[1]].append(ll[0])
        vpns = []

        v = self.cli("show vrf detail")
        for I in self.rx_line_split.split(v)[1:]:
            match = self.rx_line_name.search(I)
            name = match.group("name")
            match = self.rx_line_rd.search(I)
            rd = match.group("rd")

            vpn = {
                "type": "VRF",
                "status": True,
                "name": name,
                "interfaces": vrfif.get(name, []),
                "rd": rd
            }
            vpns += [vpn]

        return vpns
