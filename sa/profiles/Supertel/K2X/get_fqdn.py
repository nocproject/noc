# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Supertel.K2X.get_fqdn"
    interface = IGetFQDN

    rx_hostname = re.compile(r"^System Name\s*:\s*(?P<hostname>\S+)$",
                             re.MULTILINE)
    rx_domain_name = re.compile(
        r"^Default domain\s*:\s*(?P<domain>\S+)", re.MULTILINE)

    def execute(self):
        fqdn = ''
        v = self.cli("show hosts")
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
            match = self.rx_domain_name.search(v)
            if match:
                fqdn = fqdn + '.' + match.group("domain")
        return fqdn
