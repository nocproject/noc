# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetPortchannel
import re


class Script(BaseScript):
    name = "DLink.DGS3100.get_portchannel"
    interface = IGetPortchannel
    rx_trunk = re.compile(
        r"Group ID\s+:\s+(?P<trunk>\d+)\n"
        r"Member Port\s+:\s*(?P<members>\S+)*\n"
        r"Active Port\s+:\s*(?P<active>\S+)*\n"
        r"Status\s+:\s+(?P<status>\S+)\s+", re.MULTILINE | re.DOTALL)
    rx_type = re.compile(
        r"create link_aggregation group_id (?P<group_id>\d+) "
        r"type (?P<type>\S+)\s+", re.MULTILINE | re.DOTALL)

    def execute(self):
        try:
            c = self.cli("show link_aggregation")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        for match in self.rx_trunk.finditer(c):
            if match.group("status").lower() == "enable" \
            and match.group("members") is not None:
                r += [{
                    "interface": "ch%s" % match.group("trunk"),
                    "members": self.expand_interface_range(
                        self.profile.open_brackets(match.group("members"))),
                    "type": "S"
                    }]
        if len(r) > 0:
            try:
                t = self.cli("show config running")
                for match in self.rx_type.finditer(t):
                    if match.group("type") == "lacp":
                        for i in r:
                            if i["interface"] == "ch" + match.group("group_id"):
                                i["type"] = "L"
            except self.CLISyntaxError:
                pass
                
        return r
