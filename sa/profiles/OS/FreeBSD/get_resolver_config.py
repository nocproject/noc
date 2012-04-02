# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.get_resolver_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetResolverConfig
import re


class Script(NOCScript):
    name = "OS.FreeBSD.get_resolver_config"
    implements = [IGetResolverConfig]
    rx_domain = re.compile(r"^\s*domain\s+(?P<domain>\S+)")
    rx_search = re.compile(r"^\s*search\s+(?P<search>.+)")
    rx_nameserver = re.compile(r"^\s*nameserver\s+(?P<server>\S+)")

    def execute(self):
        try:
            s = self.cli("cat /etc/resolv.conf")
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
