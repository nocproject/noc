# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP

class Script(BaseScript):
    name = "Juniper.JUNOS.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<mac>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})\s+"
        r"(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
        r"(?P<interface>\S+)"
    )

    def execute(self, vrf=None):
        if not vrf:
            vrf = "default"
        return self.cli(
            "show arp no-resolve vpn %s" % vrf,
            list_re=self.rx_line
        )
