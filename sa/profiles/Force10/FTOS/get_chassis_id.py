# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Force10.FTOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Force10.FTOS.get_chassis_id"
    cache = True
    interface = IGetChassisID


    def execute(self, **kwargs):
        if self.is_s:
            return self.execute_s()
        else:
            return self.execute_other()

    #
    # S-Series
    #
    rx_system_id = re.compile(r"Stack MAC\s+:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    def execute_s(self):
        """
        S-series
        :return:
        """

=======
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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
from noc.sa.profiles.Force10.FTOS import SSeries


class Script(NOCScript):
    name = "Force10.FTOS.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    ##
    ## S-Series
    ##
    rx_system_id = re.compile(r"Stack MAC\s+:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    @NOCScript.match(SSeries)
    def execute_s(self):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        v = self.cli("show system brief")
        match = self.re_search(self.rx_system_id, v)
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }

<<<<<<< HEAD
    #
    # C/E-series
    #
    rx_chassis_id = re.compile(r"Chassis MAC\s+:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    def execute_other(self):
        """
        C/E-series
        :return:
        """
=======
    ##
    ## C/E-series
    ##
    rx_chassis_id = re.compile(r"Chassis MAC\s+:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    @NOCScript.match()
    def execute_other(self):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        v = self.cli("show chassis brief")
        match = self.re_search(self.rx_chassis_id, v)
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
