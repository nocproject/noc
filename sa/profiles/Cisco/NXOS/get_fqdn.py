# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Cisco.NXOS.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Cisco.NXOS.get_fqdn"
    interface = IGetFQDN
    rx_hostname = re.compile(r"^hostname\s+(?P<hostname>\S+)", re.MULTILINE)
    rx_domain_name = re.compile(r"^ip domain[ \-]name\s+(?P<domain>\S+)", re.MULTILINE)

    def execute(self):
        if self.has_snmp():
=======
##----------------------------------------------------------------------
## Cisco.NXOS.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetFQDN


class Script(NOCScript):
    name = "Cisco.NXOS.get_fqdn"
    implements = [IGetFQDN]
    rx_hostname = re.compile(r"^hostname\s+(?P<hostname>\S+)", re.MULTILINE)

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                # sysName.0
                v = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
                if v:
<<<<<<< HEAD
                    return v
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show running-config | include ^(hostname|ip.domain.name)")
        fqdn = []
        match = self.rx_hostname.search(v)
        if match:
            fqdn += [match.group("hostname")]
        match = self.rx_domain_name.search(v)
        if match:
            fqdn += [match.group("domain")]
        return ".".join(fqdn)
=======
                   return v
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show running-config | include hostname")
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
        return fqdn
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
