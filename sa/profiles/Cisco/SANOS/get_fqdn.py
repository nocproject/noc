# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.SANOS.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Cisco.SANOS.get_fqdn"
    interface = IGetFQDN
    rx_hostname = re.compile(r"^switchname\s+(?P<hostname>\S+)", re.MULTILINE)
    rx_domain_name = re.compile(r"^ip domain[ \-]name\s+(?P<domain>\S+)",
        re.MULTILINE)

    def execute(self):
        if self.has_snmp():
            try:
                # sysName.0
                v = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
                if v:
                   return v
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show running-config | i switchname")
        fqdn = []
        match = self.rx_hostname.search(v)
        if match:
            fqdn += [match.group("hostname")]
        v = self.cli("show running-config | i domain-name")
        match = self.rx_domain_name.search(v)
        if match:
            fqdn += [match.group("domain")]
        return ".".join(fqdn)
