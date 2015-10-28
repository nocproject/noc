# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SMB.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetFQDN


class Script(BaseScript):
    name = "Cisco.SMB.get_fqdn"
    interface = IGetFQDN
    rx_hostname = re.compile(r"System Name:\s+(?P<hostname>\S+)")

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
        match = self.rx_hostname.search(v)
        fqdn = [match.group("hostname")]
        return fqdn
