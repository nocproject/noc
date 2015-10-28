# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.IronWare.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetFQDN


class Script(BaseScript):
    """
    Get switch FQDN
    @todo: find more clean way
    """
    name = "Brocade.IronWare.get_fqdn"
    interface = IGetFQDN

    rx_hostname = re.compile(r"^hostname\s+(?P<hostname>\S+)", re.MULTILINE)
    rx_domain_name = re.compile(r"^ip domain-name\s+(?P<domain>\S+)",
                                re.MULTILINE)

    def execute(self):
        v = self.cli("show running-config | include ^(hostname|ip domain-name)")
        fqdn = []
        match = self.rx_hostname.search(v)
        if match:
            fqdn += [match.group("hostname")]
        match = self.rx_domain_name.search(v)
        if match:
            fqdn += [match.group("domain")]
        return ".".join(fqdn)
