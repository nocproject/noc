# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetFQDN


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_fqdn"
    interface = IGetFQDN

    rx_hostname = re.compile(r"^System Name\s+:\s+(?P<hostname>\S+)$",
                            re.MULTILINE)

    def execute(self):
        fqdn = ""
        v = self.cli("show system-information")
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
        return fqdn
