# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# NSN.hiX56xx.get_vlans
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re


class Script(BaseScript):
    name = "NSN.hiX56xx.get_vlans"
    interface = IGetVlans
=======
##----------------------------------------------------------------------
## NSN.hiX56xx.get_vlans
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans
import re


class Script(NOCScript):
    name = "NSN.hiX56xx.get_vlans"
    implements = [IGetVlans]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_vlan = re.compile(r"^\s(?P<vlanid>\d+)\s+\|\s+(?P<vlanname>\S+)$",
        re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan properties")):
            name = match.group("vlanname")
            vlan_id = int(match.group("vlanid"))
            if name == "<noname>":
                r += [{
                    "vlan_id": vlan_id
                }]
            else:
                r += [{
                    "vlan_id": vlan_id,
                    "name": name
                }]
        return r
