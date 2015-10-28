# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.GbE2.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re

rx_vlan_line = re.compile(r"^(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s")


class Script(BaseScript):
    name = "HP.GbE2.get_vlans"
    interface = IGetVlans

    def execute(self):
        r = self.cli("/i/l2/vlan", list_re=rx_vlan_line)
        self.cli("/")
        return r
