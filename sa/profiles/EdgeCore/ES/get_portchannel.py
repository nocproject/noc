# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel


class Script(NOCScript):
    name = "EdgeCore.ES.get_portchannel"
    implements = [IGetPortchannel]
    cache = True

    rx_chan_line_3526 = re.compile(r"Information of (?P<interface>Trunk \d+).*?Member Ports(|\s+): (?P<members_str>[^\n]+)", re.IGNORECASE | re.DOTALL | re.MULTILINE)

    @NOCScript.match(platform__contains="4612")
    @NOCScript.match(platform__contains="3526")
    @NOCScript.match(platform__contains="3510")
    @NOCScript.match(platform__contains="2228N")
    @NOCScript.match(platform__contains="3528")
    @NOCScript.match(platform__contains="3552")
    @NOCScript.match(platform__contains="ECS4210")
    def execute_3526(self):
        status = self.cli("show interface status")
        r = []
        for match in self.rx_chan_line_3526.finditer(status):
            members = match.group("members_str").strip().rstrip(",").replace("Eth", "Eth ")
            r += [{
                "interface": match.group("interface"),
                "members": members.split(", "),
                "type": "S"
            }]
        return r

    rx_chan_line_4626 = re.compile(r"Port-group number : (?P<number>\d+)", re.IGNORECASE | re.MULTILINE)
    rx_memb_line_4626 = re.compile(r"\n\d+\s+(?P<member>\S+)\s+(?P<mode>[^\n]+)", re.IGNORECASE | re.DOTALL | re.MULTILINE)

    @NOCScript.match(platform__contains="4626")
    def execute_4626(self):
        channels = self.cli("show port-group brief")
        r = []
        for match in self.rx_chan_line_4626.finditer(channels):
            details = self.cli("show port-group %s port-channel" % match.group("number"))
            r += [{
                "interface": "Port-Channel" + match.group("number"),
                "members": [memb.group("member") for memb in self.rx_memb_line_4626.finditer(details)],
                "type": "S",  # <!> TODO: port-channel type detection
            }]
        return r

    @NOCScript.match()
    def execute_other(self):
        raise self.NotSupportedError()
