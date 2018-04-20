# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# HP.GbE2.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
=======
##----------------------------------------------------------------------
## HP.GbE2.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetARP
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import re

rx_line = re.compile(r"^\s*(?P<ip>\d+\.\d+\.\d+\.\d+).+?(?P<mac>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})\s+\d+\s+(?P<interface>\S+)")


<<<<<<< HEAD
class Script(BaseScript):
    name = "HP.GbE2.get_arp"
    interface = IGetARP
=======
class Script(noc.sa.script.Script):
    name = "HP.GbE2.get_arp"
    implements = [IGetARP]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        r = self.cli("/i/l3/arp/dump", list_re=rx_line)
        self.cli("/")
        return r
