# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Dell.Powerconnect62xx.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
import re


class Script(BaseScript):
=======
##----------------------------------------------------------------------
## Dell.Powerconnect62xx.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
import re


class Script(NOCScript):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    name = "Dell.Powerconnect62xx.get_chassis_id"
    cache = True
    rx_mac = re.compile(r"Burned In MAC Address\.+ (?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)
<<<<<<< HEAD
    interface = IGetChassisID
=======
    implements = [IGetChassisID]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        match = self.re_search(self.rx_mac, self.cli("show tech-support",
            cached=True))
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
