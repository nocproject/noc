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
        cmd = "hostname -f 2>/dev/null; domainname -f 2>/dev/null; "
        cmd += "uname -n 2>/dev/null; hostname 2>/dev/null"
        hostname = self.cli(cmd)
        match = self.rx_hostname.search(hostname)
        if not match:
            raise Exception("Not implemented")
        else:
            return [match.group("hostname")]
