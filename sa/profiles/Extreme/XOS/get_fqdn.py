# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.XOS.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Extreme.XOS.get_fqdn"
    interface = IGetFQDN
    rx_hostname = re.compile(r"^SysName:\s+(?P<hostname>\S+)", re.MULTILINE)
    rx_domain_name = re.compile(r"^ip domain[ \-]name\s+(?P<domain>\S+)",
                                re.MULTILINE)

    def execute_snmp(self):
        v = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
        if v:
            return v

    def execute_cli(self):
        if self.has_snmp():
            try:
                # sysName.0
                v = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
                if v:
                    return v
            except self.snmp.TimeOutError:
                pass
        v = self.cli(
            "show switch | include SysName")
        fqdn = []
        match = self.rx_hostname.search(v)
        if match:
            fqdn += [match.group("hostname")]
        match = self.rx_domain_name.search(v)
        if match:
            fqdn += [match.group("domain")]
        return ".".join(fqdn)
