# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# OS.FreeBSD.get_vlans
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
    name = "OS.FreeBSD.get_vlans"
    interface = IGetVlans
=======
##----------------------------------------------------------------------
## OS.FreeBSD.get_vlans
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
    name = "OS.FreeBSD.get_vlans"
    implements = [IGetVlans]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_vlan = re.compile(
        r"^\tvlan: (?P<vlanid>[1-9]\d*) parent interface: \S+", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(
            self.cli("ifconfig -v", cached=True)):
            r += [{"vlan_id": int(match.group('vlanid'))}]
        return r
