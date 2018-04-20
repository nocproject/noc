# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# AlliedTelesis.AT9900.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT9900.get_vlans"
    interface = IGetVlans
    rx_vlan = re.compile(
        r"Name \.+ (?P<vlanname>\S+)\n Identifier \.+ (?P<vlanid>\d+)\n")
=======
##----------------------------------------------------------------------
## AlliedTelesis.AT9900.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans
import re


class Script(NOCScript):
    name = "AlliedTelesis.AT9900.get_vlans"
    implements = [IGetVlans]
    rx_vlan = re.compile(r"Name \.+ (?P<vlanname>\S+)\n Identifier \.+ (?P<vlanid>\d+)\n")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            r.append({
                "vlan_id": int(match.group('vlanid')),
                "name": match.group('vlanname')
            })
        return r
