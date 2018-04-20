# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Force10.FTOS.get_arp
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
## Force10.FTOS.get_arp
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

rx_line = re.compile(
    r"^Internet\s+(?P<ip>\S+)\s+\d+\s+(?P<mac>\S+)\s+(?P<interface>\S+\s+\S+)")


<<<<<<< HEAD
class Script(BaseScript):
    name = "Force10.FTOS.get_arp"
    interface = IGetARP
=======
class Script(noc.sa.script.Script):
    name = "Force10.FTOS.get_arp"
    implements = [IGetARP]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        return self.cli("show arp", list_re=rx_line)
