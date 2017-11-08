# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------
# Siklu.EH.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Siklu.EH.get_fqdn"
    interface = IGetFQDN
    rx_hostname = re.compile(r"^system\sname\s+:\s*(?P<hostname>\S+)\n", re.MULTILINE)

    def execute(self):
        if self.has_snmp():
            try:
                # sysName.0
                v = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
                if v:
                    return v
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show system")
        fqdn = []
        match = self.rx_hostname.search(v)
        if match:
            fqdn += [match.group("hostname")]
        return ".".join(fqdn)
