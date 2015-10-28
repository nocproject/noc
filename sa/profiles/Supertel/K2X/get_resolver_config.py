# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_resolver_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetResolverConfig


class Script(BaseScript):
    name = "Supertel.K2X.get_resolver_config"
    interface = IGetResolverConfig

    rx_search = re.compile(r"^Default domain:\s+(?P<search>\S+)\s*$",
                           re.MULTILINE)
    rx_nameserver = re.compile(r"^Name servers \(Preference order\):\s+"
                               r"(?P<server>.+)\s*$",
                               re.MULTILINE)

    def execute(self):
        s = self.cli("show hosts").strip()
        r = {"nameservers": []}
        match = self.rx_search.search(s)
        if match:
            search = match.group("search")
            r.update({"domain": search})
            r.update({"search": [search]})
        match = self.rx_nameserver.search(s)
        if match:
            r["nameservers"] += match.group("server").strip().split(' ')
        return r
