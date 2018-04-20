# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# HP.1910.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from noc.core.script.base import BaseScript
# NOC modules
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "HP.1910.get_fqdn"
    interface = IGetFQDN
=======
##----------------------------------------------------------------------
## HP.1910.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import noc.sa.script
## NOC modules
from noc.sa.interfaces import IGetFQDN


class Script(noc.sa.script.Script):
    name = "HP.1910.get_fqdn"
    implements = [IGetFQDN]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_hostname = re.compile(r"^\s*sysname (?P<hostname>\S+)$", re.MULTILINE)
    rx_domain_name = re.compile(
        r"^domain (?P<domain>\S+)$", re.MULTILINE)

    def execute(self):
        fqdn = ''
        v = self.cli("display current-configuration")
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
            match = self.rx_domain_name.search(v)
            if match:
                fqdn = fqdn + '.' + match.group("domain")
        return fqdn
