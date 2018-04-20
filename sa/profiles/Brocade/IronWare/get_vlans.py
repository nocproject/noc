# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Brocade.IronWare.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
=======
##----------------------------------------------------------------------
## Brocade.IronWare.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Brocade.IronWare.get_vlans
    """
    name = "Brocade.IronWare.get_vlans"
<<<<<<< HEAD
    interface = IGetVlans
=======
    implements = [IGetVlans]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_vlan_line = re.compile(
        r"^\S+\s(?P<vlan_id>\d+)\,\sName\s(?P<name>[A-z0-9\-\_]+?),.+$")

    def execute(self):
        vlans = self.cli("show vlans")
        r = []
        # Replace to findall
        for l in vlans.splitlines():
            match = self.rx_vlan_line.match(l.strip())
            if match:
                vlan_id = int(match.group("vlan_id"))
                name = match.group("name")
                if name == "[None]":
                    r += [{
                        "vlan_id": vlan_id
                    }]
                else:
                    r += [{
                        "vlan_id": vlan_id,
                        "name": name
                    }]
        return r
