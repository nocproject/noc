# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DES21xx.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re


class Script(BaseScript):
    name = "DLink.DES21xx.get_vlans"
    cache = True
    interface = IGetVlans
=======
##----------------------------------------------------------------------
## DLink.DES21xx.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans
import re


class Script(NOCScript):
    name = "DLink.DES21xx.get_vlans"
    cache = True
    implements = [IGetVlans]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_vlan = re.compile(
        r"VLAN_ID:(?P<vlanid>\d+)\n(VLAN name:(?P<vlanname>\S+)\n)*",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan", cached=True)):
            d = {}
            d["vlan_id"] = int(match.group('vlanid'))
            if match.group('vlanname'):
                d["name"] = match.group('vlanname')
            r += [d]
        return r
