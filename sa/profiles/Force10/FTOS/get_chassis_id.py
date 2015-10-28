# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetChassisID
from noc.sa.profiles.Force10.FTOS import SSeries


class Script(BaseScript):
    name = "Force10.FTOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    ##
    ## S-Series
    ##
    rx_system_id = re.compile(r"Stack MAC\s+:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    @BaseScript.match(SSeries)
    def execute_s(self):
        v = self.cli("show system brief")
        match = self.re_search(self.rx_system_id, v)
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }

    ##
    ## C/E-series
    ##
    rx_chassis_id = re.compile(r"Chassis MAC\s+:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    @BaseScript.match()
    def execute_other(self):
        v = self.cli("show chassis brief")
        match = self.re_search(self.rx_chassis_id, v)
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
