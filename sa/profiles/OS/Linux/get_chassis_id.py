# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.Linux.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "OS.Linux.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    rx_bridge = re.compile(
        r"^\S+(\s|\t)+\d+\.(?P<mac>\S+)+(\s|\t)+(no|yes)+(\s|\t)+\S",
        re.MULTILINE)
    rx_ifconfig = re.compile(
        r"^\S+\s+Link encap\:Ethernet+\s+HWaddr+\s+(?P<mac>\S+)", re.MULTILINE)
    rx_ip = re.compile(
        r"^\s+link/ether\s+(?P<mac>\S+)\s+brd\s+\S", re.MULTILINE)

    def execute(self):
        match = self.rx_bridge.search(self.cli("brctl show", cached=True))
        if not match:
            match = self.rx_ifconfig.search(self.cli("ifconfig", cached=True))
        if not match:
            match = self.rx_ip.search(self.cli("ip addr", cached=True))
        if not match:
            raise Exception("Not implemented")
        return match.group("mac")
