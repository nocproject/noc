# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Juniper.JUNOS.get_fqdn"
    interface = IGetFQDN

    rx_config = re.compile(
        r"^host-name (?P<hostname>\S+);\s+"
        r"^domain-name (?P<dname>\S+);$", re.MULTILINE)

    def execute(self):
        fqdn = []
        v = self.cli("show configuration system", cached=True)
        match = self.rx_config.search(v)
        if (match.group("hostname") and match.group("dname")):
            fqdn += [match.group("hostname")]
            fqdn += [match.group("dname")]
            return ".".join(fqdn)
