# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_resolver_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetresolverconfig import IGetResolverConfig
import re


class Script(BaseScript):
    name = "Cisco.IOS.get_resolver_config"
    interface = IGetResolverConfig
    rx_domain = re.compile(r"^ip domain(?:\-|\s)name\s+(?P<domain>\S+)")
    rx_search = re.compile(r"^ip domain(?:\-|\s)list\s+(?P<search>.+)")
    rx_nameserver = re.compile(r"^ip name(?:\-|\s)server\s+(?P<server>\S+)")

    def execute(self):
        try:
            s = self.cli("show running-config | include ip (name.server|domain.name|domain.list)")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = {"nameservers": []}
        for l in s.splitlines():
            match = self.rx_domain.search(l.strip())
            if match:
                r.update({"domain": match.group("domain")})
            match = self.rx_search.search(l.strip())
            if match:
                r.update({"search": match.group("search").split()})
            match = self.rx_nameserver.search(l.strip())
            if match:
                r["nameservers"] += [match.group("server")]
        return r
