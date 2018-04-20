# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DES21xx.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
import re


class Script(BaseScript):
    name = "DLink.DES21xx.get_chassis_id"
    cache = True
    rx_ver = re.compile(r"^MAC address:(?P<id>\S+)", re.IGNORECASE | re.MULTILINE)
    interface = IGetChassisID
=======
##----------------------------------------------------------------------
## DLink.DES21xx.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
import re


class Script(NOCScript):
    name = "DLink.DES21xx.get_chassis_id"
    cache = True
    rx_ver = re.compile(r"^MAC address:(?P<id>\S+)", re.IGNORECASE | re.MULTILINE)
    implements = [IGetChassisID]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        match = self.re_search(self.rx_ver, self.cli("show switch"))
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
