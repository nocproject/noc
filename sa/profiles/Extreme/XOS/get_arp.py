# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Extreme.XOS.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Extreme.XOS.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^\S+\s+(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+\d+\s+\S+\s+"
        r"(?P<interface>\S+).+$")

    def execute(self):
        return self.cli("sh iparp", list_re=self.rx_line)
=======
##----------------------------------------------------------------------
## Extreme.XOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP

rx_line = re.compile(
    r"^\S+\s+(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+\d+\s+\S+\s+(?P<interface>\S+).+$")


class Script(NOCScript):
    name = "Extreme.XOS.get_arp"
    implements = [IGetARP]

    def execute(self):
        return self.cli("sh iparp", list_re=rx_line)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
