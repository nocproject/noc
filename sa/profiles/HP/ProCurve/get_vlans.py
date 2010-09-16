# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
import re

#rx_vlan_sep=re.compile(r"^.+?\n\s*-{4,}\s+-{4,}\s+\+\s+-{4,}\s+-{4,}\s+-{4,}\n(.+)$",re.MULTILINE|re.DOTALL)
rx_vlan_line=re.compile(r"^\s*(?P<vlan_id>\d+)\s+(?P<name>[^|]+?)\s+\|")

class Script(noc.sa.script.Script):
    name="HP.ProCurve.get_vlans"
    implements=[IGetVlans]
    def execute(self):
        return self.cli("show vlans",list_re=rx_vlan_line)
