# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Eltex.MES.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from noc.core.script.base import BaseScript
# NOC modules
from noc.sa.interfaces.igetfqdn import IGetFQDN
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.MES.get_fqdn"
    interface = IGetFQDN
=======
##----------------------------------------------------------------------
## Eltex.MES.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import noc.sa.script
## NOC modules
from noc.sa.interfaces import IGetFQDN


class Script(noc.sa.script.Script):
    name = "Eltex.MES.get_fqdn"
    implements = [IGetFQDN]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_hostname = re.compile(r"^hostname (?P<hostname>\S+)$", re.MULTILINE)
    rx_domain_name = re.compile(
        r"^ip domain name (?P<domain>\S+)$", re.MULTILINE)

<<<<<<< HEAD
    def execute_snmp(self, **kwargs):
        try:
            fqnd = self.snmp.get(mib["SNMPv2-MIB::sysName.0"])
            return fqnd
        except self.snmp.TimeOutError:
            raise self.NotSupportedError

    def execute_cli(self):
=======
    def execute(self):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        fqdn = ''
        v = self.cli("show running-config")
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
            match = self.rx_domain_name.search(v)
            if match:
                fqdn = fqdn + '.' + match.group("domain")
        return fqdn
