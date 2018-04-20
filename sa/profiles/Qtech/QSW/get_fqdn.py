# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Qtech.QSW.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from noc.core.script.base import BaseScript
# NOC modules
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Qtech.QSW.get_fqdn"
    interface = IGetFQDN
=======
##----------------------------------------------------------------------
## Qtech.QSW.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import noc.sa.script
## NOC modules
from noc.sa.interfaces import IGetFQDN


class Script(noc.sa.script.Script):
    name = "Qtech.QSW.get_fqdn"
    implements = [IGetFQDN]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_hostname = re.compile(r"^hostname (?P<hostname>\S+)$", re.MULTILINE)
    rx_domain_name = re.compile(
        r"^ip domain name (?P<domain>\S+)$", re.MULTILINE)

    def execute(self):
        fqdn = ''
        v = self.cli("show running-config")
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
            match = self.rx_domain_name.search(v)
            if match:
                fqdn = fqdn + '.' + match.group("domain")
        return fqdn
