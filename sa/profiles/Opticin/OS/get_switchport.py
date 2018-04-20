# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Opticin.OS.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport


class Script(BaseScript):
=======
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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Opticin.OS.get_switchport
    """
    name = "Opticin.OS.get_switchport"
<<<<<<< HEAD
    interface = IGetSwitchport
=======
    implements = [IGetSwitchport]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
                "status": bool(status),
                "untagged": untagged
            }
=======
                "status": status == True,
                "untagged": untagged
                }
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            r += [swport]
        return r
