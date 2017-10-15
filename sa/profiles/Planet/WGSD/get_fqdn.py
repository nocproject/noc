# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Planet.WGSD.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from noc.core.script.base import BaseScript
# NOC modules
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Planet.WGSD.get_fqdn"
    interface = IGetFQDN

    rx_hostname = re.compile(r"^hostname (?P<hostname>\S+)$", re.MULTILINE)
    rx_domain_name = re.compile(
        r"^ip domain name (?P<domain>\S+)$", re.MULTILINE)

    def execute(self):
        fqdn = ''
        # Try SNMP first
        if self.has_snmp():
            try:
                fqdn = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
                return fqdn
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        v = self.cli("show startup-config")
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
            match = self.rx_domain_name.search(v)
            if match:
                fqdn = fqdn + '.' + match.group("domain")
        return fqdn
