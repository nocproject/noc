# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.ASA.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
import re


class Script(BaseScript):
    name = "Cisco.ASA.get_portchannel"
    interface = IGetPortchannel

    # Member 0 : GigabitEthernet0/2 , Full-duplex, 1000Mb/s
    rx_po2_members = re.compile(
        r"^\s+Member\s+\d+\s+:\s+(?P<interface>.+?)\s+.*$")

    def execute(self):
        r = []
        if self.capabilities.get("Cisco | ASA | Security | Context | Mode"):
            if self.capabilities["Cisco | ASA | Security | Context | Mode"] == "multiple":
                self.cli("changeto system")
        try:
            v = self.cli("show port-channel summary")
        except self.CLISyntaxError:
            return []
        v = self.strip_first_lines(v, 7)
        if not v:
            return []
        nextinterface = False
        table = v.splitlines()
        headline = table.pop(0).split()
        table.pop(0)
        for l in table:
            row = l.split()
            interface = dict(zip(headline[:-1], row[:len(headline)-1]))
            interface['Ports'] = row[len(headline)-1:]
            members = []
            for m in interface['Ports']:
                members += [m.split("(")[0]]
            if nextinterface:
                """If Interfaces located in one row it insert add row"""
                for m in row:
                    members += [m]
                nextinterface = False
                continue

            if not row[0].isdigit():
                """If last symbol Interfaces is comma - next row
                consist only Interfaces"""
                nextinterface = True

            r += [{
                "interface": "Po %s" % interface['Group'],
                "members": members,
                "type": "L",  # <!> TODO: port-channel type detection
                }]

        return r
