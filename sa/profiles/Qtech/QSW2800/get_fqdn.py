# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Qtech.QSW2800.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN
from noc.core.mib import mib


class Script(BaseScript):
    name = "Qtech.QSW2800.get_fqdn"
    interface = IGetFQDN

    rx_hostname = re.compile(r"^hostname (?P<hostname>\S+)$", re.MULTILINE)

    def execute_snmp(self, **kwargs):
        try:
            fqnd = self.snmp.get(mib["SNMPv2-MIB::sysName.0"])
            return fqnd
        except self.snmp.TimeOutError:
            raise self.NotSupportedError

    def execute_cli(self):
        fqdn = ""
        try:
            v = self.cli("show startup-config | i hostname", cached=True)
        except self.CLISyntaxError:
            v = self.cli("show startup-config", cached=True)
=======
##----------------------------------------------------------------------
## Qtech.QSW2800.get_fqdn
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
    name = "Qtech.QSW2800.get_fqdn"
    implements = [IGetFQDN]

    rx_hostname = re.compile(r"^hostname (?P<hostname>\S+)$", re.MULTILINE)

    def execute(self):
        fqdn = ""
        v = self.cli("show running-config")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
        return fqdn
