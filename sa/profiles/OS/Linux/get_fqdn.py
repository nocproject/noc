# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.Linux.get_fqdn
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
    name = "OS.Linux.get_fqdn"
    implements = [IGetFQDN]

    rx_hostname = re.compile(r"^(?P<hostname>\S+)$", re.MULTILINE)

    def execute(self):
        hostname = self.cli("hostname -f 2>/dev/null; domainname -f 2>/dev/null; uname -n 2>/dev/null; hostname 2>/dev/null")
        match = self.rx_hostname.search(hostname)
        if not match:
            raise Exception("Not implemented")
        else:
            return [match.group("hostname")]
