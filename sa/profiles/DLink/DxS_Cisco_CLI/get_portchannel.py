# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel
import re


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.get_portchannel"
    implements = [IGetPortchannel]
    rx_line = re.compile(r"^AggregatePort (?P<port>\d+)\s+(up|down)\s+\d+\s+\S+\s+\S+\s+\S+$", re.MULTILINE)
    rx_line1 = re.compile(r"^\s+(?P<interface>\S+\s*\d+\/\d+) Link Status: (Down|Up)$", re.MULTILINE)

    def execute(self):
        r = []
        data = self.cli("show interfaces status | i AggregatePort")
        for match in self.rx_line.finditer(data):
            port = int(match.group("port"))
            members = []
            data1 = self.cli("show interfaces AggregatePort %i | i Link Status:" % port)
            for match1 in self.rx_line1.finditer(data1):
                members += [match1.group("interface")]
            r += [{
                "interface": "Ag %i" % port,
                "members": members,
                #<!> TODO: port-channel type detection
                "type": "L"
                }]
        return r
