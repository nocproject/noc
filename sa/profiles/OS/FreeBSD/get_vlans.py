# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re


class Script(BaseScript):
    name = "OS.FreeBSD.get_vlans"
    interface = IGetVlans
    rx_vlan = re.compile(
        r"^\tvlan: (?P<vlanid>[1-9]\d*) parent interface: \S+", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(
            self.cli("ifconfig -v", cached=True)):
            r += [{"vlan_id": int(match.group('vlanid'))}]
        return r
