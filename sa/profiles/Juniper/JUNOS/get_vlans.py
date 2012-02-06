# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
import re

rx_vlan_line = re.compile(r"^(?P<name>\S+)\s+(?P<vlan_id>\d{1,4})\s")


class Script(noc.sa.script.Script):
    name = "Juniper.JUNOS.get_vlans"
    implements = [IGetVlans]

    def execute(self):
        return self.cli("show vlan brief", list_re=rx_vlan_line)
