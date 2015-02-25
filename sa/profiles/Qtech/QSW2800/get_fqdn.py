# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW2800.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetFQDN


class Script(NOCScript):
    name = "Qtech.QSW2800.get_fqdn"
    implements = [IGetFQDN]

    rx_hostname = re.compile(r"^hostname (?P<hostname>\S+)$", re.MULTILINE)

    def execute(self):
        fqdn = ""
        v = self.cli("show running-config")
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
        return fqdn
