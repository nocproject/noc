# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rubytech.l2ms.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
'''
'''
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN

class Script(BaseScript):
    name = "Rubytech.l2ms.get_fqdn"
    interface = IGetFQDN
    
    rx_hostname = re.compile(r"Device Name\s+:\s(?P<hostname>\S+)\n", re.MULTILINE)

    def execute(self):
        if self.has_snmp():
            try:
                # sysName.0
                v = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
                if v:
                   return v
            except self.snmp.TimeOutError:
                pass
        
        self.cli("system")
        v = self.cli("show")

        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")

        return fqdn
