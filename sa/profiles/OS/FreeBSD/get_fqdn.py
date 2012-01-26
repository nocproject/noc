# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.FreeBSD.get_fqdn
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetFQDN
import re


class Script(NOCScript):
    name = "OS.FreeBSD.get_fqdn"
    implements = [IGetFQDN]
    rx_hostname = re.compile(r"^(?P<hostname>\S+)")

    def execute(self):
        fqdn = []
        match = self.rx_hostname.search(self.cli("hostname"))
        if match:
            fqdn += [match.group("hostname")]
        return fqdn
