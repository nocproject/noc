# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_fqdn"
    interface = IGetFQDN
=======
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetFQDN


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.get_fqdn"
    implements = [IGetFQDN]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_hostname = re.compile(r"^hostname (?P<hostname>\S+)$", re.MULTILINE)
#    rx_domain_name = re.compile(r"^ip domain-name (?P<domain>\S+)$",
#                                re.MULTILINE)

    def execute(self):
        v = self.cli("show running-config | include hostname")
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
#            match = self.rx_domain_name.search(v)
#            if match:
#                fqdn = "%s.%s" % (fqdn, match.group("domain"))
            return fqdn
        else:
            return 'None'
