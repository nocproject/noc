# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_resolver_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetresolverconfig import IGetResolverConfig
import re


class Script(BaseScript):
    name = "DLink.DxS.get_resolver_config"
    interface = IGetResolverConfig
    rx_res = re.compile(r"\s*(?P<server>\d+\S+)")

    def execute(self):
        try:
            s = self.cli("show name_server")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = { "nameservers": [] }
        for l in s.splitlines():
            match = self.rx_res.search(l.strip())
            if match:
                r["nameservers"] += [match.group("server")]
        return r
