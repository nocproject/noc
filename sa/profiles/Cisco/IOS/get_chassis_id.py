# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
from noc.lib.mac import MAC


class Script(NOCScript):
    name = "Cisco.IOS.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    ##
    ## Catalyst 2960/3560/3750/3120 on IOS SE
    ## Catalyst 2950 on IOS EA
    ## Single chassis mac
    ##
    rx_small_cat = re.compile(
        r"^Base ethernet MAC Address\s*:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    @NOCScript.match(version__regex=r"SE|EA")
    def execute_small_cat(self):
        v = self.cli("show version")
        match = self.re_search(self.rx_small_cat, v)
        base = match.group("id")
        return [{
            "first_chassis_mac": base,
            "last_chassis_mac": base
        }]

    ##
    ## Cisco Catalyst 4000/4500 Series
    ##
    rx_cat4000 = re.compile(r"MAC Base = (?P<id>\S+).+MAC Count = (?P<count>\d+)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)

    @NOCScript.match(version__regex=r"SG")
    def execute_cat4000(self):
        try:
            v = self.cli("show idprom chassis")
        except self.CLISyntaxError:
            v = self.cli("show idprom supervisor")
        match = self.re_search(self.rx_cat4000, v)
        base = match.group("id")
        count = int(match.group("count"))
        return [{
            "first_chassis_mac": base,
            "last_chassis_mac": MAC(base).shift(count - 1)
        }]

    ##
    ## Cisco Catalyst 6500 Series or Cisco router 7600 Series
    ##
    rx_cat6000 = re.compile(
        r"chassis MAC addresses:.+from\s+(?P<from_id>\S+)\s+to\s+(?P<to_id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    @NOCScript.match(version__regex=r"S[XR]")
    def execute_cat6000(self):
        v = self.cli("show catalyst6000 chassis-mac-addresses")
        match = self.re_search(self.rx_cat6000, v)
        return [{
            "first_chassis_mac": match.group("from_id"),
            "last_chassis_mac": match.group("to_id")
        }]

    ##
    ## Other
    ##
    @NOCScript.match()
    def execute_not_supported(self):
        raise self.NotSupportedError()
