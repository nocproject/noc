# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Extreme.XOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
=======
##----------------------------------------------------------------------
## Extreme.XOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re

rx_vlan_line = re.compile(r"^(?P<name>\S+)\s+(?P<vlan_id>\d{1,4})\s")


<<<<<<< HEAD
class Script(BaseScript):
    name = "Extreme.XOS.get_vlans"
    interface = IGetVlans
=======
class Script(noc.sa.script.Script):
    name = "Extreme.XOS.get_vlans"
    implements = [IGetVlans]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        vlans = self.cli("show vlan")
        r = []
        for l in vlans.split("\n"):
            match = rx_vlan_line.match(l.strip())
            if match:
                name = match.group("name")
                vlan_id = int(match.group("vlan_id"))
                r.append({
                    "vlan_id": vlan_id,
                    "name": name
                    })
        return r
