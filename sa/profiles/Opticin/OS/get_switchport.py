# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Opticin.OS.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport


class Script(BaseScript):
    """
    Opticin.OS.get_switchport
    """
    name = "Opticin.OS.get_switchport"
    interface = IGetSwitchport
    cache = True

    def execute(self):
        r = []
        # Get interfaces status
        for s in self.scripts.get_interface_status():
            name = s["interface"]
            status = s["status"]
            untagged = "1"
            swport = {
                "interface": name,
                "members": "",
                "802.1ad Tunnel": False,
                "802.1Q Enabled": False,
                "tagged": "",
                "status": status == True,
                "untagged": untagged
                }
            r += [swport]
        return r
