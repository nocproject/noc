# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Juniper.JUNOS.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^(?P<mac>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:"
        r"[0-9a-f]{2}:[0-9a-f]{2})\s+"
=======
##----------------------------------------------------------------------
## Juniper.JUNOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP

class Script(NOCScript):
    name = "Juniper.JUNOS.get_arp"
    implements = [IGetARP]

    rx_line = re.compile(
        r"^(?P<mac>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})\s+"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        r"(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
        r"(?P<interface>\S+)"
    )

    def execute(self, vrf=None):
        if not vrf:
            vrf = "default"
        return self.cli(
<<<<<<< HEAD
            "show arp no-resolve vpn %s | except demux" % vrf,
=======
            "show arp no-resolve vpn %s" % vrf,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            list_re=self.rx_line
        )
