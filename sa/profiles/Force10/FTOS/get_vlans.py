# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
# Force10.FTOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
from noc.lib.text import parse_table
import re

class Script(noc.sa.script.Script):
    name="Force10.FTOS.get_vlans"
    implements=[IGetVlans]
    def execute(self):
        return [{"vlan_id":x[0],"name":x[1]} for x in parse_table(self.cli("show vlan brief | no-more"))]
