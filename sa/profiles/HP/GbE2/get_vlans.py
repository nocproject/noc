# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# HP.GbE2.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
=======
##----------------------------------------------------------------------
## HP.GbE2.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re

rx_vlan_line = re.compile(r"^(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s")


<<<<<<< HEAD
class Script(BaseScript):
    name = "HP.GbE2.get_vlans"
    interface = IGetVlans
=======
class Script(noc.sa.script.Script):
    name = "HP.GbE2.get_vlans"
    implements = [IGetVlans]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        r = self.cli("/i/l2/vlan", list_re=rx_vlan_line)
        self.cli("/")
        return r
