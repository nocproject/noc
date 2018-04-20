# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.AOS.get_vlans
# ----------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
=======
##----------------------------------------------------------------------
## Alcatel.AOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re

rx_vlan_line = re.compile(
    r"^\s*(?P<vlan_id>\d{1,4})(\s+\S+){9}\s+o(?:n|ff)\s+(?P<name>(\S+\s*)+?)"
    r"\s*$")
rx_vlan1_line = re.compile(
    r"^\s*(?P<vlan_id>\d{1,4})(\s+\S+){9}\s+(?P<name>(\S+\s*)+?)\s*$")

<<<<<<< HEAD

class Script(BaseScript):
    name = "Alcatel.AOS.get_vlans"
    interface = IGetVlans

=======

class Script(noc.sa.script.Script):
    name = "Alcatel.AOS.get_vlans"
    implements = [IGetVlans]

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute(self):
        vlans = self.cli("show vlan")
        r = []
        for l in vlans.split("\n"):
            match = rx_vlan_line.match(l.strip())
            if match:
                r.append({
                    "vlan_id": int(match.group("vlan_id")),
                    "name": match.group("name")
                })
            else:
                match = rx_vlan1_line.match(l.strip())
                if match:
                    r.append({
                        "vlan_id": int(match.group("vlan_id")),
                        "name": match.group("name")
                    })
        return r
