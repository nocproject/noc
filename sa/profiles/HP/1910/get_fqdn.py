# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1910.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from noc.core.script.base import BaseScript
## NOC modules
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "HP.1910.get_fqdn"
    interface = IGetFQDN

    rx_hostname = re.compile(r"^\s*sysname (?P<hostname>\S+)$", re.MULTILINE)
    rx_domain_name = re.compile(
        r"^domain (?P<domain>\S+)$", re.MULTILINE)

    def execute(self):
        fqdn = ''
        v = self.cli("display current-configuration")
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
            match = self.rx_domain_name.search(v)
            if match:
                fqdn = fqdn + '.' + match.group("domain")
        return fqdn
