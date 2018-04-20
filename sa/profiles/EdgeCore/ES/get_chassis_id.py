# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# EdgeCore.ES.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "EdgeCore.ES.get_chassis_id"
    cache = True
    interface = IGetChassisID
    rx_mac_4626 = re.compile(r"\d+\s+(?P<id>\S+).*?System\s+CPU",
        re.IGNORECASE | re.MULTILINE)
    rx_mac_3528mv2 = re.compile(
        r"\sMAC\sAddress\s+\(Unit\s\d\)\s+:\s+(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)
=======
##----------------------------------------------------------------------
## EdgeCore.ES.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "EdgeCore.ES.get_chassis_id"
    cache = True
    implements = [IGetChassisID]
    rx_mac_4626 = re.compile(r"\d+\s+(?P<id>\S+).*?System\s+CPU",
        re.IGNORECASE | re.MULTILINE)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_mac = re.compile(r"MAC Address[^:]*?:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    ##
    ## ES4626
    ##
<<<<<<< HEAD
    @BaseScript.match(platform__contains="4626")
=======
    @NOCScript.match(platform__contains="4626")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute_4626(self):
        v = self.cli("show mac-address-table static")
        match = self.re_search(self.rx_mac_4626, v)
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }

    ##
    ## Other
    ##
<<<<<<< HEAD
    @BaseScript.match()
    def execute_other(self):
        if self.match_version(platform__contains="3528MV2"):
            v = self.cli("show system\n")               # ES-3538MV2
            match = self.rx_mac_3528mv2.search(v)
        else:
            v = self.cli("show system")
            match = self.re_search(self.rx_mac, v)
=======
    @NOCScript.match()
    def execute_other(self):
        v = self.cli("show system")
        match = self.re_search(self.rx_mac, v)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        first_mac = match.group("id")
        v = self.cli("show int statu")
        for l in v.splitlines():
            match = self.rx_mac.search(l)
            if match:
<<<<<<< HEAD
                if match.group("id") != first_mac:
=======
                if match.group("id")!= first_mac:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    last_mac = match.group("id")
        if not last_mac:
            last_mac = first_mac
        return {
            "first_chassis_mac": first_mac,
            "last_chassis_mac": last_mac
        }
