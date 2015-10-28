# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from noc.core.script.base import BaseScript
## NOC modules
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Eltex.MES.get_fqdn"
    interface = IGetFQDN

    rx_hostname = re.compile(r"^hostname (?P<hostname>\S+)$", re.MULTILINE)
    rx_domain_name = re.compile(
        r"^ip domain name (?P<domain>\S+)$", re.MULTILINE)

    def execute(self):
        fqdn = ''
        v = self.cli("show running-config")
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
            match = self.rx_domain_name.search(v)
            if match:
                fqdn = fqdn + '.' + match.group("domain")
        return fqdn
