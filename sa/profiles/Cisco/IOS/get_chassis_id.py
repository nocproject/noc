# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
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
    name = "Cisco.IOS.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    ##
    ## Catalyst 2960/3560/3750/3120 on IOS SE
    ## Catalyst 2950 on IOS EA
    ##
    rx_small_cat = re.compile(r"^Base ethernet MAC Address\s*:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    @NOCScript.match(version__regex=r"SE|EA")
    def execute_small_cat(self):
        v = self.cli("show version")
        match = self.re_search(self.rx_small_cat, v)
        return match.group("id")

    ##
    ## Cisco Catalyst 4000/4500 Series
    ##
    rx_cat4000 = re.compile(r"MAC Base =\s+(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    @NOCScript.match(version__regex=r"SG")
    def execute_cat4000(self):
        v = self.cli("show idprom chassis")
        match = self.re_search(self.rx_cat4000, v)
        return match.group("id")

    ##
    ## Cisco Catalyst 6500 Series or Cisco router 7600 Series
    ##
    rx_cat6000 = re.compile(r"chassis MAC addresses:.+from\s+(?P<id>\S+)\s+to",
        re.IGNORECASE | re.MULTILINE)

    @NOCScript.match(version__regex=r"S[XR]")
    def execute_cat6000(self):
        v = self.cli("show catalyst6000 chassis-mac-addresses")
        match = self.re_search(self.rx_cat6000, v)
        return match.group("id")

    ##
    ## Other
    ##
    @NOCScript.match()
    def execute_not_supported(self):
        raise self.NotSupportedError()
